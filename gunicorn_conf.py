from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/home/rezayogaswara/python_projects/chatbotstudioapi.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/home/rezayogaswara/python_projects/backend-chatbot-studio/access_log'
errorlog = '/home/rezayogaswara/python_projects/backend-chatbot-studio/error_log'
