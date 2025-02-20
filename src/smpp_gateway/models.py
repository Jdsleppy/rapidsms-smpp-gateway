from django.db import connection, models
from django.utils.functional import cached_property
from rapidsms.models import Backend


class AbstractTimestampModel(models.Model):
    create_time = models.DateTimeField()
    modify_time = models.DateTimeField()

    class Meta:
        abstract = True


class MOMessage(AbstractTimestampModel, models.Model):
    """Mobile-originated, or inbound, message."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        PROCESSING = "processing", "Processing"
        DONE = "done", "Done"

    backend = models.ForeignKey(Backend, on_delete=models.PROTECT)
    # Save the raw bytes, in case they're needed later
    short_message = models.BinaryField()
    params = models.JSONField()
    status = models.CharField(max_length=32, choices=Status.choices)

    @cached_property
    def decoded_short_message(self) -> str:
        data_coding = self.params.get("data_coding", 0)
        short_message = self.short_message.tobytes()  # type: bytes
        if data_coding == 0:
            return short_message.decode("ascii")
        if data_coding == 8:
            return short_message.decode("utf-16-be")
        raise ValueError(
            f"Unsupported data_coding {data_coding}. Short message: {short_message}"
        )

    def __str__(self):
        return f"{self.params['short_message']} ({self.id})"

    class Meta:
        verbose_name = "mobile-originated message"


class MTMessage(AbstractTimestampModel, models.Model):
    """Mobile-terminated, or outbound, message."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        ERROR = "error", "Error"

    backend = models.ForeignKey(Backend, on_delete=models.PROTECT)
    # SMPP client will decide how to encode it
    short_message = models.TextField()
    params = models.JSONField()
    status = models.CharField(max_length=32, choices=Status.choices)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == MTMessage.Status.NEW:
            with connection.cursor() as curs:
                curs.execute(f"NOTIFY {self.backend.name}")

    def __str__(self):
        return f"{self.short_message} ({self.id})"

    class Meta:
        verbose_name = "mobile-terminated message"


class MTMessageStatus(AbstractTimestampModel, models.Model):
    """Metadata and status information about outbound messages."""

    mt_message = models.ForeignKey(MTMessage, on_delete=models.CASCADE)
    backend = models.ForeignKey(Backend, on_delete=models.PROTECT)
    sequence_number = models.IntegerField(
        help_text="The initial sequence_number established by us when the message was sent."
    )
    command_status = models.IntegerField(null=True)
    message_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="The message_id we receive from the MC (via its submit_sm_resp).",
    )
    delivery_report = models.BinaryField(
        null=True,
        help_text="The delivery_report we receive from the MC (via its deliver_sm).",
    )

    @cached_property
    def delivery_report_as_bytes(self) -> bytes:
        return self.delivery_report.tobytes()

    def __str__(self):
        return f"{self.backend} ({self.sequence_number})"

    class Meta:
        verbose_name = "mobile-terminated message status"
        constraints = [
            models.UniqueConstraint(
                fields=["backend", "sequence_number"], name="unique_seq_num"
            )
        ]
