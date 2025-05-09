# process/views.py

from django.shortcuts import render

# Create your views here.

#import json
import logging
#from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult

#from process.models import Process
#from process.serializers import ProcessSerializer

from .serializers import ProcessRequestSerializer
from .tasks import process_data

#from django.http import JsonResponse
#from django.views.decorators.http import require_POS
#from .models import Message

# Import extend_schema decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

logger = logging.getLogger(__name__)

class ProcessView(APIView):
    # API endpoint to accept data and queue a background task.
    @extend_schema(
        request=ProcessRequestSerializer, # Document the request body using the serializer
        responses={
            202: {"description": "Task successfully queued",
                  "examples": [
                        OpenApiExample(
                        'Task Queued Response',
                        value={"task_id": "a1b2c3d4-e5f6-7890-1234-abcdef123456", "status": "Task queued"},
                        request_only=False, # This is a response example
                        response_only=True),
                    ]
                  },
            400: {"description":"Invalid request data"} # Document the potential bad request response
        },
        description="Accepts email and message, queues a background processing task, and returns the task ID.", # View-level description
        summary="Queue a data processing task", # Short summary
        tags=["Processing"] # Optional: Organize endpoints by tags
    )
    def post(self, request, *args, **kwargs):
        serializer = ProcessRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            message = serializer.validated_data['message']

            try:
                # Queue the task using .delay() which is a shortcut for .apply_async()
                task = process_data.delay(email, message)

                logger.info(f'Task {task.id} queued for email {email}')

                # Return the task ID and a confirmation message
                response_data = {
                    'task_id': task.id,
                    'message': 'Request received and task queued'
                }
                # 202 Accepted is suitable for async operations
                return Response(response_data, status=status.HTTP_202_ACCEPTED)

            except Exception as e:
                logger.error(f'Failed to queue task: {e}', exc_info=True)
                return Response(
                    { "errors": serializer.errors },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Return validation errors
            logger.warning(f'Invalid request data: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskStatusView(APIView):
    # API endpoint to retrieve the status and result of a background task.
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='task_id', # Parameter name in the URL
                type={'type': 'string', 'format': 'uuid'}, # Specify type and format
                location=OpenApiParameter.PATH, # It's a path parameter
                description='UUID of the Celery task.', # Description
                required=True # It's required in the path
            ),
        ],
        responses={
            200: {"description": "Task status and result",
                  "examples": [
                      OpenApiExample(
                          'Pending Status',
                          value={"task_id": "...", "status": "PENDING", "result": None, "successful": None},
                          response_only=True
                        ),
                      OpenApiExample(
                          'Success Status',
                          value={"task_id": "...", "status": "SUCCESS", "result": {"status": "success", "message": "..."}, "successful": True},
                          response_only=True
                        ),
                      OpenApiExample(
                          'Failure Status',
                          value={"task_id": "...", "status": "FAILURE", "result": "Error details...", "successful": False, "error": "Error details..."},
                          response_only=True
                        ),
                    ]},
                # You might add a 404 resonse if task_id is not found or invalid format
        },
        description="Retrieves the current status (PENDING, STARTED, SUCCESS, FAILURE) and result of a background task given its ID.",
        summary="Get task status and result",
        tags=["Processing"]
    )
    def get(self, request, task_id, *args, **kwargs):
        try:
            # Get the task result object from Celery's result backend
            task_result = AsyncResult(task_id)

            response_data = {
                'task_id': task_id,
                'status': task_result.status, # PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
                'result': None, # Will hold the task's return value or error info
            }

            if task_result.successful():
                response_data['result'] = task_result.get() # Get the return value
            elif task_result.failed():
                # Get the exception information if the task failed
                result_info = task_result.info
                # result_info could be an Exception object or the dict we returned in the task
                if isinstance(result_info, Exception):
                     response_data['result'] = {
                             'error': str(result_info), 'type': type(result_info).__name__ }
                else:
                     response_data['result'] = result_info # Use the dict returned by the task

                # Optional: Log the failure if retrieved here
                # logger.warning(f"Task {task_id} failed. Result info: {response_data['result']}")
        
            elif task_result.status == 'PENDING':
                response_data['result'] = {
                        'info': 'Task is waiting to be processed or is currently processing.' }
            elif task_result.status == 'STARTED':
                 response_data['result'] = {'info': 'Task has started processing.'}
            elif task_result.status == 'PROCESSING': # Custom state from update_state
                response_data['result'] = task_result.info # Get the metadata {'progress': 50}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle potential errors retrieving task status (
            #e.g., invalid task_id format, backend connection issue)
            logger.error(f"Error retrieving status for task {task_id}: {e}", exc_info=True)
            return Response(
                {"error": "Could not retrieve task status.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#class TaskStatusAPIView(APIView):
#    def get(self, request, task_id):
#        result = AsyncResult(task_id)
#        response_data = {
#            "task_id": task_id,
#            "status": result.status,
#            "result": str(result.result) if result.successful() else ""
#        }
#        serializer = StatusResponseSerializer(response_data)

#        return Response(serializer.data)

#class ProcessMessageView(APIView):
#    def post(self, request):
#        serializer = MessageSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#@api_view(['POST'])
#def process_endpoint(request):
#    serializer = ProcessDataSerializer(data=request.data)
#    if serializer.is_valid():
#        task = process_data_task.delay(serializer.validated_data)
#        return Response({"task_id": task.id,
#                         "message": "Processing request in the background."},
#                        status=status.HTTP_202_ACCEPTED)
#    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#@api_view(['GET'])
#def task_status(request, task_id):
#    task = AsyncResult(task_id)
#    if task.state == 'PENDING':
#        response_data = {
#            'state': task.state,
#            'info': 'Task is pending...'

#        }
#    elif task.state != 'FAILURE':
#        response_data = {
#            'state': task.state,
#            'result': task.info,
#        }
#    else:
#        response_data = {
#            'state': task.state,
#            'error': str(task.info),
#        }
#    return Response(response_data)


#@api_view(['GET','POST'])
#def process_list(request):

    #List all process, or create a new process
#   if request.method == 'GET':
#       process = Process.objects.all()

#       serializer = ProcessSerializer(process, many=True)
#       return Response(serializer.data)

#   elif request.method == 'POST':
#       serializer = ProcessSerializer(data=request.data)
#       if serializer.is_valid():
#           serializer.save()
#           return Response(serializer.data,
#                           status=status.HTTP_201_CREATED)
#       return Response(serializer.errors,
#                       status=status.HTTP_400_BAD_REQUEST)

#@api_view(['GET','PUT','PATCH','DELETE'])
#def process_detail(request, pk):
#   try:
#       process = Process.objects.get(pk=pk)
#   except Process.DoesNotExist:
#       return Response(status=status.HTTP_404_NOT_FOUND)

#   if request.method == 'GET':
#       serializer = ProcessSerializer(process)
#       return Response(serializer.data)

#   elif request.method == 'PUT':
#       serializer = ProcessSerializer(process, data=request.data)

#       if serializer.is_valid():
#           serializer.save()
#           return Response(serializer.data)
#       return Response(serializer.errors,
#                       status=status.HTTP_400_BAD_REQUEST)
#   elif request.method == 'PATCH':
#       serializer = ProcessSerializer(process,
#                                       data=request.data,
#                                       partial=True)

#       if serializer.is_valid():
#           serializer.save()
#           return Response(serializer.data)
#       return Response(serializer.errors,
#                       status=status.HTTP_400_BAD_REQUEST)

#   elif request.method == 'DELETE':
#       process.delete()
#       return Response(status=status.HTTP_204_NO_CONTENT)


