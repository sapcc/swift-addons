class DomainOverrideMiddleware(object):
    def __init__(self, app):
        self.app = app

    @classmethod
    def factory(cls, global_config, **local_config):
        def _factory(app):
            return cls(app, **local_config)

        return _factory

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)
