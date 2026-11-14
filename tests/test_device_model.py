from django.test import TestCase, TransactionTestCase
from django.db import close_old_connections
from concurrent.futures import ThreadPoolExecutor
from django.db import transaction, connection
from inventory.models import Device, DeviceStatus, DeviceCounter
from unittest.mock import patch
from django.db.models import Model
from threading import Event
from threading import Barrier
from django.db import OperationalError
from django.db.models import F
from django.db import IntegrityError
from django.db.transaction import TransactionManagementError
from psycopg.errors import SerializationFailure
from functools import wraps
from typing import Callable
from inspect import signature
from django.db import DatabaseError
from datetime import datetime, timezone
from django.utils import timezone as t_zone

def retry(times: int = 3, exc_types=(Exception,)):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            bound = signature(fn).bind_partial(*args, **kwargs)
            callback = bound.arguments.get("call_back")
            #s = bound.arguments.get("self")
            last = None
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exc_types as e:
                    if not is_serialization_failure(e): #s.is_serialization_failure(e):
                        raise 
                    last = e
                    if attempt < times and callback is not None:
                        callback()
            raise last
        return wrapper
    return  decorator

def is_serialization_failure(exc: Exception) -> bool:
    if isinstance(exc, SerializationFailure):
        return True

    cause = exc.__cause__
    context = exc.__context__

    if cause is not None:
        return is_serialization_failure(cause) #self.is_serialization_failure(cause)

    if context is not None:
        return is_serialization_failure(context) #self.is_serialization_failure(context)

    return False

def is_serialization_failure_only_cause(exc: Exception) -> bool:
    if exc.__cause__ is None:
        return isinstance(exc, SerializationFailure)

    return (
            isinstance(exc, SerializationFailure)
            or is_serialization_failure(exc.__cause__) #self.is_serialization_failure(exc.__cause__)
        )

class DeviceModelTest(TestCase):

    def test_devices_are_ordered_numerically(self):
        Device.objects.create(device_id="device-999")
        Device.objects.create(device_id="device-1000")
        Device.objects.create(device_id="device-1001")
        Device.objects.create(device_id="device-998")

        device_ids = list(
            Device.objects.values_list("device_id", flat=True)
        )

        self.assertEqual(
            device_ids,
            ["device-998", "device-999", "device-1000", "device-1001"],
        )

    def test_filtered_devices_are_ordered_numerically(self):
        Device.objects.create(device_id="device-1000", state=DeviceStatus.ONLINE)
        Device.objects.create(device_id="device-999", state=DeviceStatus.ONLINE)
        Device.objects.create(device_id="device-1001", state=DeviceStatus.OFFLINE)

        device_ids = list(
            Device.objects
            .filter(state=DeviceStatus.ONLINE)
            .values_list("device_id", flat=True)
        )

        self.assertEqual(device_ids, ["device-999", "device-1000"])
    
    def test_device_str_representation(self):
        Device.objects.create()
        Device.objects.create(firmware_version="2.0.0", state=DeviceStatus.ONLINE)
        device = Device.objects.get(pk="device-001")
        assert str(device) == f"Device:\nid: device-001\nversion: 1.0.0\nstate: Offline"
        device = Device.objects.get(pk="device-002")
        assert str(device) == f"Device:\nid: device-002\nversion: 2.0.0\nstate: Online"

    def test_device_last_seen_at_stores_aware_datetime(self):
        last_seen = datetime(2026, 11, 14, 12, 30, 0, tzinfo=timezone.utc)
        device = Device.objects.create(last_seen_at=last_seen)
        device = Device.objects.get(pk=device.device_id)
        assert str(device.last_seen_at) == "2026-11-14 12:30:00+00:00"
        assert t_zone.is_aware(device.last_seen_at)
        assert device.last_seen_at == last_seen

    def test_filter_devices_by_state(self):
        device1 = Device.objects.create(state=DeviceStatus.ONLINE)
        device2 = Device.objects.create(state=DeviceStatus.ONLINE)
        device3 = Device.objects.create()
        devices_online = [(dev.device_id, dev.state) for dev in Device.objects.filter(state=DeviceStatus.ONLINE).all()]
        assert len(devices_online) == 2
        assert [dev[1] for dev in devices_online] == [DeviceStatus.ONLINE, DeviceStatus.ONLINE]

    def test_duplicate_device_id_raises_integrity_error(self):
        device = Device.objects.create()
        count = Device.objects.count()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Device.objects.create(device_id=device.device_id)
        assert Device.objects.count() == count
        self.assertEqual(Device.objects.count(), count)

    def test_device_id_is_generated_from_current_sequence(self):
        
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL DeviceCounter-based ID generation")
        counter = DeviceCounter.objects.get(pk=1)
        initial_value = counter.next_value

        device = Device.objects.create()

        assert initial_value == 0
        assert device.device_id == "device-001"
        assert Device.objects.count() == 1
        assert DeviceCounter.objects.get(pk=1).next_value == 1
        counter = DeviceCounter.objects.get(pk=1)
        initial_value = counter.next_value
        assert initial_value == 1
        
    def test_first_device_gets_device_id_001(self):
        device = Device.objects.create()

        assert device.device_id == "device-001"

    def test_devices_get_sequential_ids(self):
        device_1 = Device.objects.create()
        device_2 = Device.objects.create()
        device_3 = Device.objects.create()

        assert device_1.device_id == "device-001"
        assert device_2.device_id == "device-002"
        assert device_3.device_id == "device-003"

    def test_device_has_correct_default_values(self):
        device = Device.objects.create()

        assert device.firmware_version == "1.0.0"
        assert device.state == DeviceStatus.OFFLINE
        assert device.last_seen_at is None

        assert device.created_at is not None
        assert device.updated_at is not None

    def test_update_device_does_not_change_device_id(self):
        device = Device.objects.create()
        original_device_id = device.device_id
        assert original_device_id == "device-001"
        assert device.firmware_version == "1.0.0"
        device.firmware_version = "2.0.0"
        device.save()

        device.refresh_from_db()

        assert device.device_id == original_device_id
        assert device.firmware_version == "2.0.0"

    def test_device_counter_increments_on_creation(self):
        
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL DeviceCounter updates")
        counter = DeviceCounter.objects.get(pk=1)
        initial_value = counter.next_value

        Device.objects.create()

        counter.refresh_from_db()

        assert counter.next_value == initial_value + 1

    def test_device_counter_does_not_increment_on_update(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL DeviceCounter updates")

        device = Device.objects.create()

        counter = DeviceCounter.objects.get(pk=1)
        initial_value = counter.next_value

        device.firmware_version = "2.0.0"
        device.save()

        counter.refresh_from_db()

        assert counter.next_value == initial_value

    def test_device_counter_matches_created_devices(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL DeviceCounter updates")

        initial_counter = DeviceCounter.objects.get(pk=1).next_value
        initial_count = Device.objects.count()

        for _ in range(5):
            Device.objects.create()

        counter = DeviceCounter.objects.get(pk=1)
        devices_count = Device.objects.count()

        assert counter.next_value == initial_counter + 5
        assert devices_count == initial_count + 5

    def test_device_ids_are_unique_and_sequential(self):
        devices = [Device.objects.create() for _ in range(10)]

        device_ids = [device.device_id for device in devices]

        assert len(device_ids) == len(set(device_ids))
        assert device_ids == [
            f"device-{number:03d}"
            for number in range(1, 11)
        ]

    def test_device_id_supports_numbers_above_999(self):
        for number in range(1, 1000):
            Device.objects.create()

        device = Device.objects.create()

        assert device.device_id == "device-1000"


    def test_device_id_after_deleting_device(self):
        device_1 = Device.objects.create()
        device_2 = Device.objects.create()
        device_3 = Device.objects.create()

        device_2.delete()

        device_4 = Device.objects.create()

        assert device_1.device_id == "device-001"
        assert device_3.device_id == "device-003"
        assert device_4.device_id == "device-004"

    def test_saving_existing_device_does_not_create_new_device(self):
        device = Device.objects.create()
        original_id = device.device_id
        initial_count = Device.objects.count()

        device.firmware_version = "2.0.0"
        device.save()

        assert Device.objects.count() == initial_count
        assert device.device_id == original_id

    def test_device_counter_rolls_back_when_device_creation_fails(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL DeviceCounter transaction handling")

        initial_counter = DeviceCounter.objects.get(pk=1).next_value
        initial_count = Device.objects.count()

        with patch.object(Model, "save", side_effect=Exception("Simulated database error")):
            with self.assertRaisesRegex(Exception, "Simulated database error"):
                Device.objects.create()

        assert initial_counter == DeviceCounter.objects.get(pk=1).next_value
        assert initial_count == Device.objects.count()

class DeviceSharedDataTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device1 = Device.objects.create(
            firmware_version="1.0.0",
            state=DeviceStatus.ONLINE,
        )
        cls.device2 = Device.objects.create(
            firmware_version="2.0.0",
            state=DeviceStatus.ONLINE,
        )
        cls.device3 = Device.objects.create(
            firmware_version="3.0.0",
            state=DeviceStatus.OFFLINE,
        )

    def test_set_up_test_data_creates_three_devices(self):
        self.assertEqual(Device.objects.count(), 3)

    def test_shared_devices_have_expected_values(self):
        self.assertEqual(self.device1.device_id, "device-001")
        self.assertEqual(self.device1.firmware_version, "1.0.0")
        self.assertEqual(self.device1.state, DeviceStatus.ONLINE)

        self.assertEqual(self.device2.device_id, "device-002")
        self.assertEqual(self.device2.firmware_version, "2.0.0")
        self.assertEqual(self.device2.state, DeviceStatus.ONLINE)

        self.assertEqual(self.device3.device_id, "device-003")
        self.assertEqual(self.device3.firmware_version, "3.0.0")
        self.assertEqual(self.device3.state, DeviceStatus.OFFLINE)

    def test_shared_devices_can_be_filtered_by_state(self):
        online_devices = Device.objects.filter(state=DeviceStatus.ONLINE)
        offline_devices = Device.objects.filter(state=DeviceStatus.OFFLINE)

        self.assertEqual(online_devices.count(), 2)
        self.assertEqual(offline_devices.count(), 1)

class DeviceConcurrencyTest(TransactionTestCase):
    #print("Database name:", connection.settings_dict["NAME"])
    #print("Database test settings:", connection.settings_dict.get("TEST"))
    #print("Transaction mode:", connection.settings_dict["OPTIONS"])
    def setUp(self):
        DeviceCounter.objects.get_or_create(
            pk=1,
            defaults={"next_value": 0}
        )

    def test_concurrent_device_creation_generates_unique_ids(self):
        barrier = Barrier(5)
        def create_device(_):
            close_old_connections()
            #from django.db import connections
            #db_connection = connections["default"]

            #print(
            #    "Worker database:",
            #    db_connection.settings_dict["NAME"],
            #    "Connection:",
            #    db_connection.connection,
            #)
            barrier.wait()
            try:
                device = Device.objects.create()
                return device.device_id
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as executor:
            device_ids = list(executor.map(create_device, range(5)))

        assert len(device_ids) == 5
        assert len(set(device_ids)) == 5

        assert sorted(device_ids) == [
            "device-001",
            "device-002",
            "device-003",
            "device-004",
            "device-005",
        ]

class DeviceTransactionTest(TransactionTestCase):
    def setUp(self):
        DeviceCounter.objects.get_or_create(
            pk=1,
            defaults={"next_value": 0}
        )
    
    def test_device_counter_lock_is_released_after_rollback(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL row-level locking and rollback")
        self.setUp()
        initial_counter = DeviceCounter.objects.get(pk=1).next_value
        initial_count = Device.objects.count()
        with patch.object(Model, "save", side_effect=Exception("Simulated database error")):
            with self.assertRaisesRegex(Exception, "Simulated database error"):
                Device.objects.create()
        assert initial_counter == DeviceCounter.objects.get(pk=1).next_value
        assert initial_count == Device.objects.count()
        
        device = Device.objects.create()
        assert device.device_id == f"device-{initial_counter + 1:03d}"
        assert DeviceCounter.objects.get(pk=1).next_value == initial_counter + 1
        assert Device.objects.count() == initial_count + 1

class DeviceIsolationTest(TransactionTestCase):

    def setUp(self):
        DeviceCounter.objects.get_or_create(
            pk=1,
            defaults={"next_value": 100}
        )

    def test_read_committed_allows_non_repeatable_read(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL READ COMMITTED isolation")
        t1_read = Event()
        t2_committed = Event()

        results = {}

        def transaction_1():
            close_old_connections()
            try:
                with transaction.atomic():
                    counter = DeviceCounter.objects.get(pk=1)
                    results["first_read"] = counter.next_value

                    t1_read.set()
                    assert t2_committed.wait(timeout=10)

                    counter.refresh_from_db()
                    results["second_read"] = counter.next_value
            finally:
                close_old_connections()

        def transaction_2():
            close_old_connections()
            try:
                assert t1_read.wait(timeout=10)

                with transaction.atomic():
                    DeviceCounter.objects.filter(pk=1).update(
                        next_value=110
                    )

                t2_committed.set()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(transaction_1)
            future_2 = executor.submit(transaction_2)

            future_1.result(timeout=15)
            future_2.result(timeout=15)

        assert results["first_read"] == 100
        assert results["second_read"] == 110

    def test_repeatable_read_prevents_non_repeatable_read(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL REPEATABLE READ isolation")
        t1_read = Event()
        t2_committed = Event()

        results = {}

        def transaction_1():
            close_old_connections()
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"
                                        )
                        counter = DeviceCounter.objects.get(pk=1)
                        results["first_read"] = counter.next_value

                        t1_read.set()
                        assert t2_committed.wait(timeout=10)

                        counter.refresh_from_db()
                        results["second_read"] = counter.next_value
            finally:
                close_old_connections()

        def transaction_2():
            close_old_connections()
            try:
                assert t1_read.wait(timeout=10)

                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"
                                        )
                        DeviceCounter.objects.filter(pk=1).update(
                            next_value=110
                        )

                t2_committed.set()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(transaction_1)
            future_2 = executor.submit(transaction_2)

            future_1.result(timeout=15)
            future_2.result(timeout=15)

        assert results["first_read"] == 100
        assert results["second_read"] == 100     

    def test_repeatable_read_prevents_concurrent_update(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL REPEATABLE READ isolation")
        t1_read = Event()
        t2_committed = Event()

        results = {}

        def transaction_1():
            close_old_connections()
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"
                                        )
                        counter = DeviceCounter.objects.get(pk=1)
                        results["first_read"] = counter.next_value

                        t1_read.set()
                        assert t2_committed.wait(timeout=10)

                        counter.refresh_from_db()
                        results["second_read"] = counter.next_value
                        DeviceCounter.objects.filter(pk=1).update(
                                                                        next_value=120
                                                                    )
            finally:
                close_old_connections()

        def transaction_2():
            close_old_connections()
            try:
                assert t1_read.wait(timeout=10)

                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"
                                        )
                        DeviceCounter.objects.filter(pk=1).update(
                            next_value=110
                        )

                t2_committed.set()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(transaction_1)
            future_2 = executor.submit(transaction_2)

            with self.assertRaises(OperationalError):
                future_1.result(timeout=15)
            future_2.result(timeout=15)

        assert results["first_read"] == 100
        assert results["second_read"] == 100 
        assert DeviceCounter.objects.get(pk=1).next_value == 110

    def test_f_expression_prevents_lost_update(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL transaction isolation setup")
        t1_read = Event()
        t2_committed = Event()

        results = {}

        def transaction_1():
            close_old_connections()
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL READ COMMITTED"
                                        )
                        counter = DeviceCounter.objects.get(pk=1)
                        results["first_read"] = counter.next_value

                        t1_read.set()
                        assert t2_committed.wait(timeout=10)

                        counter.refresh_from_db()
                        results["second_read"] = counter.next_value
                        DeviceCounter.objects.filter(pk=1).update(
                                                                        next_value=F("next_value") + 10
                                                                    )
                        counter = DeviceCounter.objects.get(pk=1)
                        results["third_read"] = counter.next_value
            finally:
                close_old_connections()

        def transaction_2():
            close_old_connections()
            try:
                assert t1_read.wait(timeout=10)

                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL READ COMMITTED"
                                        )
                        DeviceCounter.objects.filter(pk=1).update(
                            next_value=F("next_value") + 10
                        )

                t2_committed.set()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(transaction_1)
            future_2 = executor.submit(transaction_2)

            future_1.result(timeout=15)
            future_2.result(timeout=15)

        assert results["first_read"] == 100
        assert results["second_read"] == 110
        assert results["third_read"] == 120 
        assert DeviceCounter.objects.get(pk=1).next_value == 120

    def test_select_for_update_prevents_lost_update(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL row-level locking")
        t1_read = Event()
        t2_committed = Event()
        t2_started = Event()
        t2_started_continue = Event()

        results = {}

        def transaction_1():
            close_old_connections()
            try:
                
                with transaction.atomic():
                    
                    counter = DeviceCounter.objects.select_for_update().get(pk=1)
                    results["first_read"] = counter.next_value
                    counter.next_value += 10
                    t1_read.set()
                    assert t2_started.wait(timeout=10)
                    assert not t2_started_continue.wait(timeout=5)
                    assert not t2_committed.is_set()
                    counter.save()
                    counter.refresh_from_db()
                    results["second_read"] = counter.next_value
                                                                    
            finally:
                close_old_connections()

        def transaction_2():
            close_old_connections()
            try:
                assert t1_read.wait(timeout=10)

                with transaction.atomic():
                    t2_started.set()
                    counter = DeviceCounter.objects.select_for_update().get(pk=1)
                    t2_started_continue.set()
                    results["third_read"] = counter.next_value
                    counter.next_value += 10
                    counter.save()
                    counter.refresh_from_db()
                    results["fourth_read"] = counter.next_value
                t2_committed.set()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(transaction_1)
            future_2 = executor.submit(transaction_2)

            future_1.result(timeout=15)
            future_2.result(timeout=15)

        assert results["first_read"] == 100
        assert results["second_read"] == 110
        assert results["third_read"] == 110
        assert results["fourth_read"] == 120
        assert DeviceCounter.objects.get(pk=1).next_value == 120

    def test_select_for_update_nowait_raises_error(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL SELECT FOR UPDATE NOWAIT")
        t1_read = Event()
        t2_committed = Event()
        t2_started = Event()
        t2_started_continue = Event()

        results = {}

        def transaction_1():
            close_old_connections()
            try:
                
                with transaction.atomic():
                    
                    counter = DeviceCounter.objects.select_for_update(nowait=True).get(pk=1)
                    results["first_read"] = counter.next_value
                    counter.next_value += 10
                    t1_read.set()
                    assert t2_started.wait(timeout=10)
                    assert not t2_started_continue.wait(timeout=5)
                    assert not t2_committed.is_set()
                    counter.save()
                    counter.refresh_from_db()
                    results["second_read"] = counter.next_value
                                                                    
            finally:
                close_old_connections()

        def transaction_2():
            close_old_connections()
            try:
                assert t1_read.wait(timeout=10)

                with transaction.atomic():
                    t2_started.set()
                    counter = DeviceCounter.objects.select_for_update(nowait=True).get(pk=1)
                    t2_started_continue.set()
                    results["third_read"] = counter.next_value
                    counter.next_value += 10
                    counter.save()
                    counter.refresh_from_db()
                    results["fourth_read"] = counter.next_value
                t2_committed.set()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(transaction_1)
            future_2 = executor.submit(transaction_2)

            future_1.result(timeout=15)
            with self.assertRaises(OperationalError):
                future_2.result(timeout=15)

        assert results["first_read"] == 100
        assert results["second_read"] == 110
        assert "third_read" not in results
        assert "fourth_read" not in results
        assert DeviceCounter.objects.get(pk=1).next_value == 110

class DeviceSkipLockedTest(TransactionTestCase):

    def setUp(self):

        for i in range(5):
            DeviceCounter.objects.get_or_create(
                pk=i + 1,
                defaults={"next_value": 100 + i}
            )

    def test_select_for_update_skip_locked_skips_locked_rows(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL SELECT FOR UPDATE SKIP LOCKED")
        t1_locked = Event()
        t2_started = Event()
        t2_finished = Event()
        t1_continue = Event()
        t3_end = Event()


        results = {}

        def transaction_1():
            close_old_connections()
            try:
                
                with transaction.atomic():
                    
                    counter1 = DeviceCounter.objects.select_for_update(skip_locked=True).get(pk=1)
                    counter2 = DeviceCounter.objects.select_for_update(skip_locked=True).get(pk=4)
                    t1_locked.set()
                    assert t2_started.wait(timeout=10)
                                                        
            finally:
                close_old_connections()
                t1_continue.set()


        def transaction_3():
            close_old_connections()
            try:
                assert t2_finished.wait(timeout=20)

                with transaction.atomic():
                    
                    jobs_all = DeviceCounter.objects.select_for_update(skip_locked=True).all()
                    jobs_two = DeviceCounter.objects.select_for_update(skip_locked=True).order_by("pk")[:2]
                    results["5_third"] = DeviceCounter.objects.select_for_update(skip_locked=True).filter(pk=5).first()
                    results["1_all_third"] = DeviceCounter.objects.select_for_update(skip_locked=True).filter(pk=1).first()
                    results["jobs_all_third"] = [dc.next_value for dc in list(jobs_all)]
                    results["jobs_two_third"] = [dc.next_value for dc in list(jobs_two)]
                    t3_end.set()

            finally:
                close_old_connections()


        def transaction_2():
            close_old_connections()
            try:
                assert t1_locked.wait(timeout=10)

                with transaction.atomic():
                    
                    jobs_all = DeviceCounter.objects.select_for_update(skip_locked=True).all()
                    jobs_two = DeviceCounter.objects.select_for_update(skip_locked=True).order_by("pk")[:2]
                    results["jobs_all_first"] = [dc.next_value for dc in list(jobs_all)]
                    results["jobs_two_first"] = [dc.next_value for dc in list(jobs_two)]
        
                    t2_started.set()
                    assert t1_continue.wait(timeout=10)
                    jobs_all = DeviceCounter.objects.select_for_update(skip_locked=True).all()
                    jobs_two = DeviceCounter.objects.select_for_update(skip_locked=True).order_by("pk")[:2]
                    results["jobs_all_second"] = [dc.next_value for dc in list(jobs_all)]
                    results["jobs_two_second"] = [dc.next_value for dc in list(jobs_two)]
                    t2_finished.set()
                    assert t3_end.wait(timeout=20)

            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_1 = executor.submit(transaction_1)
            future_2 = executor.submit(transaction_2)
            future_3 = executor.submit(transaction_3)

            future_1.result(timeout=30)
            future_2.result(timeout=30)
            future_3.result(timeout=30)

            assert results["5_third"] == None
            assert results["1_all_third"] == None
            assert results["jobs_all_third"] == []
            assert results["jobs_two_third"] == []
            assert results["jobs_all_first"] == [101, 102, 104]
            assert results["jobs_two_first"] == [101, 102]
            assert results["jobs_all_second"] == [100, 101, 102, 103, 104]
            assert results["jobs_two_second"] == [100, 101]

class DeviceDeadlockTest(TransactionTestCase):

    def setUp(self):

        for i in range(2):
            DeviceCounter.objects.get_or_create(
                pk=i + 1,
                defaults={"next_value": 100 + i}
            )


    def test_select_for_update_detects_deadlock(self):
        t1_first = Event()
        
        t2_first = Event()
        
    
        results = {}

        def transaction_1():
            close_old_connections()
            try:
                
                with transaction.atomic():
                    
                    counter1 = DeviceCounter.objects.select_for_update().get(pk=1).next_value
                    t1_first.set()
                    t2_first.wait(timeout=10)

                    counter2 = DeviceCounter.objects.select_for_update().get(pk=2).next_value
                    
                    results["first"] = counter1 if counter1 else None
                    results["second"] = counter2 if counter2 else None
                                                        
            finally:
                close_old_connections()
                

        def transaction_2():
            close_old_connections()
            try:
                assert t1_first.wait(timeout=10)

                with transaction.atomic():

                    counter1 = DeviceCounter.objects.select_for_update().get(pk=2).next_value
                    t2_first.set()
                    counter2 = DeviceCounter.objects.select_for_update().get(pk=1).next_value
                    results["third"] = counter1 if counter1 else None
                    results["fourth"] = counter2 if counter2 else None

            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(transaction_1)
            future_2 = executor.submit(transaction_2)

            
            future_1.result(timeout=15)
            with self.assertRaises(OperationalError):
                future_2.result(timeout=15)

            assert results == {'first': 100, 'second': 101}

class DeviceAtomicSavepointTest(TransactionTestCase):

    def setUp(self):

        for i in range(3):
            DeviceCounter.objects.get_or_create(
                pk=i + 1,
                defaults={"next_value": 100 + i}
            )


    def test_nested_atomic_commits_successfully(self):

        with transaction.atomic():
            
            DeviceCounter.objects.filter(pk=1).update(next_value=110)

            try:
                with transaction.atomic():
                    DeviceCounter.objects.filter(pk=2).update(next_value=111)
                    
            except ValueError:
                pass

            DeviceCounter.objects.filter(pk=3).update(next_value=112)

        assert DeviceCounter.objects.get(pk=1).next_value == 110
        assert DeviceCounter.objects.get(pk=2).next_value == 111
        assert DeviceCounter.objects.get(pk=3).next_value == 112

    def test_nested_atomic_rolls_back_to_savepoint(self):   
        with transaction.atomic():
            
            DeviceCounter.objects.filter(pk=1).update(next_value=110)

            try:
                with transaction.atomic():
                    DeviceCounter.objects.filter(pk=2).update(next_value=111)
                    raise ValueError("Something went wrong")
    
            except ValueError:
                pass

            DeviceCounter.objects.filter(pk=3).update(next_value=112)

        assert DeviceCounter.objects.get(pk=1).next_value == 110
        assert DeviceCounter.objects.get(pk=2).next_value == 101
        assert DeviceCounter.objects.get(pk=3).next_value == 112

    def test_nested_atomic_exception_rolls_back_outer_transaction(self):
        with self.assertRaisesRegex(ValueError, "Something went wrong"):
            with transaction.atomic():
                        
                DeviceCounter.objects.filter(pk=1).update(next_value=110)

                        
                with transaction.atomic():
                    DeviceCounter.objects.filter(pk=2).update(next_value=111)
                    raise ValueError("Something went wrong")
                

                DeviceCounter.objects.filter(pk=3).update(next_value=112)

        assert DeviceCounter.objects.get(pk=1).next_value == 100
        assert DeviceCounter.objects.get(pk=2).next_value == 101
        assert DeviceCounter.objects.get(pk=3).next_value == 102

    def test_catching_exception_inside_atomic_marks_transaction_for_rollback(self):
        with transaction.atomic():
                        
            DeviceCounter.objects.filter(pk=1).update(next_value=110)

                        
            with transaction.atomic():
                try:
                    DeviceCounter.objects.filter(pk=2).update(next_value=111)
                    raise ValueError("Something went wrong")
                except ValueError:
                    pass

                DeviceCounter.objects.filter(pk=3).update(next_value=112)
            DeviceCounter.objects.filter(pk=1).update(next_value=113)

        assert DeviceCounter.objects.get(pk=1).next_value == 113
        assert DeviceCounter.objects.get(pk=2).next_value == 111
        assert DeviceCounter.objects.get(pk=3).next_value == 112

    def test_integrity_error_inside_atomic_marks_transaction_for_all_rollback(self):
        with self.assertRaises(TransactionManagementError):
            with transaction.atomic():
                            
                DeviceCounter.objects.filter(pk=1).update(next_value=110)

                            
                with transaction.atomic():
                    try:
                        DeviceCounter.objects.filter(pk=2).update(next_value=111)
                        DeviceCounter.objects.create(pk=1, next_value=999)
                    except IntegrityError:
                        pass

                    DeviceCounter.objects.filter(pk=3).update(next_value=112)
                DeviceCounter.objects.filter(pk=1).update(next_value=113)

        assert DeviceCounter.objects.get(pk=1).next_value == 100
        assert DeviceCounter.objects.get(pk=2).next_value == 101
        assert DeviceCounter.objects.get(pk=3).next_value == 102

    def test_integrity_error_inside_atomic_marks_transaction_for_rollback(self):
        
        with transaction.atomic():
                            
            DeviceCounter.objects.filter(pk=1).update(next_value=110)

                            
            with transaction.atomic():
                try:
                    DeviceCounter.objects.filter(pk=2).update(next_value=111)
                    DeviceCounter.objects.create(pk=1, next_value=999)
                except IntegrityError:
                    pass

                with self.assertRaises(TransactionManagementError):
                    DeviceCounter.objects.filter(pk=3).update(next_value=112)
                
            DeviceCounter.objects.filter(pk=1).update(next_value=113)

        assert DeviceCounter.objects.get(pk=1).next_value == 113
        assert DeviceCounter.objects.get(pk=2).next_value == 101
        assert DeviceCounter.objects.get(pk=3).next_value == 102

    def test_integrity_error_inside_atomic_marks_transaction_for_rollback_try_out(self):
        with transaction.atomic():

            DeviceCounter.objects.filter(pk=1).update(next_value=110)

            try:
                with transaction.atomic():
                    try:
                        DeviceCounter.objects.filter(pk=2).update(next_value=111)
                        DeviceCounter.objects.create(pk=1, next_value=999)
                    except IntegrityError:
                        pass

                    DeviceCounter.objects.filter(pk=3).update(next_value=112)

            except TransactionManagementError:
                pass

            DeviceCounter.objects.filter(pk=1).update(next_value=113)
            assert DeviceCounter.objects.get(pk=1).next_value == 113
            assert DeviceCounter.objects.get(pk=2).next_value == 101
            assert DeviceCounter.objects.get(pk=3).next_value == 102

    def test_nested_atomic_without_savepoint_rolls_back_outer_transaction(self):
        with transaction.atomic():
                        
            DeviceCounter.objects.filter(pk=1).update(next_value=110)

            try:           
                with transaction.atomic(savepoint=False):
                    
                    DeviceCounter.objects.filter(pk=2).update(next_value=111)
                    raise ValueError("Something went wrong")
                    
                
            except ValueError:
                pass
            with self.assertRaises(TransactionManagementError):
                DeviceCounter.objects.filter(pk=3).update(next_value=112)

        assert DeviceCounter.objects.get(pk=1).next_value == 100
        assert DeviceCounter.objects.get(pk=2).next_value == 101
        assert DeviceCounter.objects.get(pk=3).next_value == 102

    def test_manual_savepoint_rollback(self):
        with transaction.atomic():
            DeviceCounter.objects.filter(pk=1).update(next_value=110)
            sid = transaction.savepoint()
            DeviceCounter.objects.filter(pk=2).update(next_value=111)
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            DeviceCounter.objects.filter(pk=3).update(next_value=112)
            transaction.savepoint_commit(sid)
            DeviceCounter.objects.filter(pk=1).update(next_value=120)

        assert DeviceCounter.objects.get(pk=1).next_value == 120
        assert DeviceCounter.objects.get(pk=2).next_value == 101
        assert DeviceCounter.objects.get(pk=3).next_value == 112

    def test_nested_atomic_without_savepoint_integrity_error_rolls_back_outer_transaction(self):
        with transaction.atomic():

            DeviceCounter.objects.filter(pk=1).update(next_value=21)

            try:
                with transaction.atomic(savepoint=False):

                    DeviceCounter.objects.filter(pk=1).update(next_value=22)

                    DeviceCounter.objects.create(
                        pk=1,
                        next_value=999
                    )

            except IntegrityError:
                pass

        assert DeviceCounter.objects.get(pk=1).next_value == 100

    def test_nested_atomic_without_savepoint_inside_atomic_rolls_back_outer_transaction(self):
        with transaction.atomic():

            DeviceCounter.objects.filter(pk=1).update(next_value=110)

            try:
                with transaction.atomic():

                    DeviceCounter.objects.filter(pk=1).update(next_value=120)

                    with transaction.atomic(savepoint=False):

                        DeviceCounter.objects.filter(pk=1).update(next_value=130)

                        DeviceCounter.objects.create(
                            pk=1,
                            next_value=999
                        )

            except IntegrityError:
                pass

        assert DeviceCounter.objects.get(pk=1).next_value == 110


class DeviceSerializableIsolationTest(TransactionTestCase):

    def setUp(self):

        for i in range(3):
            DeviceCounter.objects.get_or_create(
                pk=i + 1,
                defaults={"next_value": 100}
            )

    def test_serializable_isolation_raises_serialization_failure(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL SERIALIZABLE isolation")
        barrier = Barrier(2)
        def transaction_1():
            close_old_connections()
            try:
                
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"
                                        )
                        counter1 = DeviceCounter.objects.get(pk=1).next_value
                        counter2 = DeviceCounter.objects.get(pk=2).next_value
                        barrier.wait()
                        if (counter1 + counter2) >= 150:
                            DeviceCounter.objects.filter(pk=1).update(
                                                                        next_value=F("next_value") - 100
                                                                    )
            finally:
                close_old_connections()

        def transaction_2():
            close_old_connections()
            try:
                
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"
                                        )
                        counter1 = DeviceCounter.objects.get(pk=1).next_value
                        counter2 = DeviceCounter.objects.get(pk=2).next_value
                        barrier.wait()
                        if (counter1 + counter2) >= 150:
                            DeviceCounter.objects.filter(pk=2).update(
                                                                        next_value=F("next_value") - 100
                                                                    )
            finally:
                close_old_connections()

        transaction_1_failed = False
        transaction_2_failed = False

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(transaction_1)
            future_2 = executor.submit(transaction_2)
            exc1 = None
            exc2 = None
            try:
                future_1.result(timeout=15)
            except OperationalError as error:
                transaction_1_failed = True
                exc1 = error

            try:
                future_2.result(timeout=15)
            except OperationalError as error:
                transaction_2_failed = True
                exc2 = error

        assert transaction_1_failed != transaction_2_failed

        counter1 = DeviceCounter.objects.get(pk=1).next_value
        counter2 = DeviceCounter.objects.get(pk=2).next_value

        assert (counter1, counter2) in [(0, 100), (100, 0)]

        exc = exc1 if (exc1 is not None) else exc2

        assert isinstance(exc.__cause__, SerializationFailure)
        
class DeviceSerializationRetryTest(TransactionTestCase):

    def setUp(self):
    
        for i in range(3):
            DeviceCounter.objects.get_or_create(
                pk=i + 1,
                defaults={"next_value": 100}
            )

    
    @retry(times=3, exc_types=(Exception,))
    def call_retry(self, fn: Callable, call_back: Callable | None = None):
        return fn()

    def get_next_value(self, attempts: list[int], i: int, up: int = 0) -> int:
            attempts[0] += 1
            if attempts[0] < up:
                raise SerializationFailure("Serialization Erro")
            return DeviceCounter.objects.get(pk=i).next_value
    
    def test_serialization_retry_succeeds_without_retry(self):
        
        attempts = [0,]

        next_value = self.call_retry(lambda: self.get_next_value(attempts, 1))

        assert attempts[0] == 1
        assert next_value == 100


    def test_serialization_retry_succeeds_on_second_attempt(self):

        attempts = [0,]
        
        next_value = self.call_retry(lambda: self.get_next_value(attempts, 1, 2))

        assert attempts[0] == 2
        assert next_value == 100


    def test_serialization_retry_raises_after_max_attempts(self):

        attempts = [0,]

        with self.assertRaisesRegex(SerializationFailure, "Serialization Erro"):
            self.call_retry(lambda: self.get_next_value(attempts, 1, 4))

        assert attempts[0] == 3

    def update_counter(self, attempts: list[int]) -> int:
        with transaction.atomic():
            counter = DeviceCounter.objects.get(pk=1).next_value
            attempts[0] += 1
            if attempts[0] == 1:
                raise SerializationFailure("Serialization Erro")
            if attempts[0] == 2:
                DeviceCounter.objects.filter(pk=1).update(next_value = 200)
            return counter

    def call_back_update_counter(self, i: int) -> None:
        with transaction.atomic():
            DeviceCounter.objects.filter(pk=i).update(next_value = 150)
     
    def test_serialization_retry_restarts_entire_transaction(self):

        attempts = [0,]
        assert DeviceCounter.objects.get(pk=1).next_value == 100
        next_value_maybe_old = self.call_retry(lambda: self.update_counter(attempts), 
                                               lambda: self.call_back_update_counter(1))

        assert attempts[0] == 2
        assert next_value_maybe_old == 150
        assert DeviceCounter.objects.get(pk=1).next_value == 200

    def test_operational_error_contains_serialization_failure(self):
        excpt = None
        try:
            try:
                raise SerializationFailure()
            except SerializationFailure as error:
                raise OperationalError() from error
        except OperationalError as exc:
            excpt = exc

        assert isinstance(excpt, OperationalError)
        assert isinstance(excpt.__cause__, SerializationFailure)

    def test_is_serialization_failure_detects_context(self):
        excpt = None
        try:
            try:
                raise SerializationFailure()
            except SerializationFailure:
                raise OperationalError()
        except OperationalError as exc:
            excpt = exc

        assert isinstance(excpt, OperationalError)
        assert excpt.__cause__ is None
        assert isinstance(excpt.__context__, SerializationFailure)
        assert is_serialization_failure(excpt) #self.is_serialization_failure(excpt)

    def test_is_serialization_failure_detects_nested_cause(self):
        excpt = None

        try:
            try:
                raise SerializationFailure()
            except SerializationFailure as error:
                try:
                    raise DatabaseError() from error
                except DatabaseError as db_error:
                    raise OperationalError() from db_error

        except OperationalError as exc:
            excpt = exc

        assert isinstance(excpt, OperationalError)
        assert isinstance(excpt.__cause__, DatabaseError)
        assert isinstance(excpt.__cause__.__cause__, SerializationFailure)

        assert is_serialization_failure(excpt) #self.is_serialization_failure(excpt)

    def test_is_serialization_failure_returns_false_for_integrity_error(self):
        excpt = None
        try:
            raise IntegrityError()
        except IntegrityError as exc:
            excpt = exc    

        assert not is_serialization_failure(excpt) #self.is_serialization_failure(excpt) 

    def test_is_serialization_failure_returns_false_for_nested_integrity_error(self):
        excpt = None

        try:
            try:
                raise IntegrityError()
            except IntegrityError as error:
                raise OperationalError() from error

        except OperationalError as exc:
            excpt = exc

        assert isinstance(excpt, OperationalError)
        assert isinstance(excpt.__cause__, IntegrityError)
        assert not is_serialization_failure(excpt) #self.is_serialization_failure(excpt)

    def update_counter_2(self, attempts: list[int]) -> int:
        with transaction.atomic():
            counter = DeviceCounter.objects.get(pk=1).next_value
            attempts[0] += 1
            if attempts[0] == 1:
                try:
                    raise SerializationFailure("Serialization Erro")
                except SerializationFailure as error:
                    raise OperationalError("Operational Error::Serialization Erro") from error
            if attempts[0] == 2:
                DeviceCounter.objects.filter(pk=1).update(next_value = 200)
            return counter


    def test_retry_recognizes_wrapped_serialization_failure(self):
        attempts = [0,]

        next_value = self.call_retry(lambda: self.update_counter_2(attempts))

        assert attempts[0] == 2
        assert next_value == 100
        assert DeviceCounter.objects.get(pk=1).next_value == 200

    def update_counter_3(self, attempts: list[int]) -> int:
        with transaction.atomic():
            counter = DeviceCounter.objects.get(pk=1).next_value
            attempts[0] += 1
            if attempts[0] == 1:
                try:
                    raise IntegrityError("Integrity Erro")
                except IntegrityError as error:
                    raise OperationalError("Operational Error::Integrity Error") from error
            if attempts[0] == 2:
                DeviceCounter.objects.filter(pk=1).update(next_value = 200)
            return counter

    def test_retry_does_not_retry_wrapped_integrity_error(self):
        attempts = [0,]

        with self.assertRaisesRegex(OperationalError, "Operational Error::Integrity Error") as exc:
            self.call_retry(lambda: self.update_counter_3(attempts))

        assert isinstance(exc.exception, OperationalError)
        assert isinstance(exc.exception.__cause__, IntegrityError)
        assert attempts[0] == 1
        
class DeviceRealSerializationRetryTest(TransactionTestCase):
    
    def setUp(self):
        
        for i in range(5):
            DeviceCounter.objects.get_or_create(
                pk=i + 1,
                defaults={"next_value": 100}
            )
    
    @retry(times=3, exc_types=(Exception,))
    def call_retry(self, fn: Callable, call_back: Callable | None = None):
        return fn()
    
    def test_retry_restarts_transaction_after_real_serialization_failure(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL SERIALIZABLE isolation and serialization failures")
        barrier = Barrier(2)
        flag = [True, True]
        read_count = [0, 0]
        def transaction_1():
            close_old_connections()
            try:
                
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"
                                        )
                        counter1 = DeviceCounter.objects.get(pk=1).next_value
                        counter2 = DeviceCounter.objects.get(pk=2).next_value
                        read_count[0] += 1
                        if flag[0]:
                            flag[0] = False 
                            barrier.wait()
                        if (counter1 + counter2) >= 150:
                            DeviceCounter.objects.filter(pk=1).update(
                                                                        next_value=F("next_value") - 100
                                                                    )
            finally:
                close_old_connections()

        def transaction_2():
            close_old_connections()
            try:
                
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                                            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"
                                        )
                        counter1 = DeviceCounter.objects.get(pk=1).next_value
                        counter2 = DeviceCounter.objects.get(pk=2).next_value
                        read_count[1] += 1
                        if flag[1]:
                            flag[1] = False
                            barrier.wait()
                        if (counter1 + counter2) >= 150:
                            DeviceCounter.objects.filter(pk=2).update(
                                                                        next_value=F("next_value") - 100
                                                                    )
            finally:
                close_old_connections()

        transaction_1_failed = False
        transaction_2_failed = False

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(lambda: self.call_retry(transaction_1))
            future_2 = executor.submit(lambda: self.call_retry(transaction_2))
            
            exc1 = None
            exc2 = None
            
            try:
                future_1.result(timeout=15)
            except OperationalError as error:
                transaction_1_failed = True
                exc1 = error

            try:
                future_2.result(timeout=15)
            except OperationalError as error:
                transaction_2_failed = True
                exc2 = error

        assert transaction_1_failed == False 
        assert transaction_2_failed == False
        assert exc1 is None
        assert exc2 is None
                
        counter1 = DeviceCounter.objects.get(pk=1).next_value
        counter2 = DeviceCounter.objects.get(pk=2).next_value

        assert (counter1, counter2) in [(0, 100), (100, 0)]

        assert tuple(read_count) in {(1, 2), (2, 1)}

    def test_retry_calls_callback_between_attempts(self):
        attemps = [0]

        def call_serializationfailure():
            raise SerializationFailure()

        def attems_up():
            attemps[0] += 1

        with self.assertRaises(SerializationFailure):
            self.call_retry(call_serializationfailure, attems_up)

        assert attemps[0] == 2

    
    def test_retry_stops_when_callback_raises_exception(self):
        attemps = [0]

        def call_serializationfailure():
            raise SerializationFailure()

        def attems_up():
            attemps[0] += 1
            raise ValueError()
            
        with self.assertRaises(ValueError):
            self.call_retry(call_serializationfailure, attems_up)

        assert attemps[0] == 1 

    
