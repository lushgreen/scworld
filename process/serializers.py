from rest_framework import serializers
#from process.models import Process
#from .models import Message

class ProcessRequestSerializer(serializers.Serializer):
    # Serializer for validating the incoming POST request data.
    email = serializers.EmailField(required=True)
    message = serializers.CharField(
        required=True,
        max_length=500,
        help_text="Message content for the task. Max 500 characters." # Add help_text
    )

    # You can add more complex validation if needed
    #def validate_message(self, value):
    #   if "spam" in value.lower():
    #       raise serializers.ValidationError("Message content seems like spam.")
    #   return value

class StatusResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    status = serializers.CharField()
    result = serializers.CharField(allow_blank=True, default='')

#class ProcessSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Process
#        fields = "__all__"

#class ProcessDataSerializer(serializers.Serializer):
#    email = serializers.EmailField()
#    message = serializers.CharField()

#class MessageSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Message
#        fields = ['email', 'message']

