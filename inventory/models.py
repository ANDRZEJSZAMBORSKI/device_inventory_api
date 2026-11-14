from django.db import models
from django.db.models.functions import Cast, Substr
from django.db.models import IntegerField
from django.db import transaction
from django.db import connection

class DeviceStatus(models.TextChoices):
    ONLINE = "online", "Online"
    OFFLINE = "offline", "Offline"
    DFU_IN_PROGRESS = "dfu_in_progress", "Dfu_in_progress"

class DeviceQuerySet(models.QuerySet):
    def ordered_by_device_number(self):
        return (
            self.annotate(
                device_number=Cast(
                    Substr("device_id", 8),
                    IntegerField(),
                )
            )
            .order_by("device_number")
        )

class DeviceCounter(models.Model):
    next_value = models.PositiveBigIntegerField(default=0)

class Device(models.Model):
    device_id = models.CharField(
                                    max_length=20,
                                    primary_key=True,
                                    editable=False,
                                )
    firmware_version = models.CharField(max_length=10, default="1.0.0") 
    state = models.CharField(
                                max_length=20,
                                choices=DeviceStatus.choices,
                                default=DeviceStatus.OFFLINE,
                            )
    last_seen_at = models.DateTimeField(auto_now_add=False, null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"
        ordering = [
            Cast(Substr("device_id", 8), IntegerField()).asc()
        ]

    def __str__(self):
        return f"Device:\nid: {self.device_id}\nversion: {self.firmware_version}\nstate: {self.get_state_display()}"

    def save(self, *args, **kwargs):

        def scal(number: int) -> int:
            number_ = number
            k = 3
            c = 1
            while (number_:= number_ // 10) > 0:
                c += 1
            if c > k:
                k = c 
            return k
                            
        
        with transaction.atomic():
            if not self.device_id:
                if connection.vendor == "sqlite":
                
                    last_device = (
                                        Device.objects
                                        .annotate(
                                            device_number=Cast(Substr("device_id", 8), IntegerField())
                                        )
                                        .order_by("-device_number")
                                        .first()
                                    ) #Device.objects.order_by("-device_id").first()
                    number = last_device.device_number + 1 if last_device else 1 #int(last_device.device_id.split("-")[1]) + 1 if last_device else 1
                    
                elif connection.vendor == "postgresql":
                    counter = DeviceCounter.objects.select_for_update().get(pk=1)
                    counter.next_value += 1
                    counter.save(update_fields=["next_value"])
                    number = counter.next_value
            
                k = scal(number)   
                self.device_id = f"device-{number:0{k}d}"   
            super().save(*args, **kwargs)
