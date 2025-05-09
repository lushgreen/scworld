# process/urls.py
from django.urls import path
from .views import ProcessView, TaskStatusView

#from process import views 
#from . import views
#from .views import ProcessMessageView

urlpatterns = [

    path('process/',
         ProcessView.as_view(),
         name = 'process_data'),

    #path('status/<uuid:task_id>/',
    path('status/<str:task_id>/',
         TaskStatusView.as_view(),
         name = 'task_status'),

#    path('message/',
#         ProcessMessageView.as_view(),
#         name='process_message'),

#    path('submit/',
#         views.process_endpoint,
#         name = 'process_endpoint'),

#    path('taskstatus/<str:task_id>/',
#         views.task_status,
#         name = 'task_status'),


#    path('process/',
#       views.process_list,
#       name = 'process-list'),

#   path('process/<int:pk>/',
#       views.process_detail,
#       name = 'process-detail'),

]


