# app/config/config_loader.py

import os

def load_config(app):
    """
    Load the configuration for the app based on the environment.
    """
    config_type = os.environ.get('FLASK_ENV', 'development')

    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

    config_mapping = {
        'production': 'app.config.config.ProductionConfig',
        'testing': 'app.config.config.TestingConfig',
        'development': 'app.config.config.DevelopmentConfig'
    }

    config_class = config_mapping.get(config_type, 'app.config.config.DevelopmentConfig')
    app.config.from_object(config_class)

