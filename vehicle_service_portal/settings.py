from .settings_envs.base import *

deployment = env.str('DEPLOYMENT_ENV')

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT',
                               default=True)
if deployment.lower() in ['prod', 'production', 'release']:
    from .settings_envs.production import *
elif deployment.lower() in ['test', 'testing', 'qa']:
    from .settings_envs.qa import *
elif deployment.lower() in ['dev', 'develop', 'development']:
    from .settings_envs.development import *
