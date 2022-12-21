from pickle import FALSE
from .settings_envs.base import *
import os

deployment = env.str('DEPLOYMENT_ENV')

#env.bool('SECURE_SSL_REDIRECT',default=False)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT',default=False)

# This code does not work. It does not redirect based on the variable above deployment. Text this section to make it work

if deployment.lower() in ['prod', 'production', 'release']:
    from .settings_envs.production import *
elif deployment.lower() in ['test', 'testing', 'qa']:
    from .settings_envs.qa import *
elif deployment.lower() in ['dev', 'develop', 'development']:
    from .settings_envs.development import *


