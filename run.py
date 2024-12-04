"""
Main application entry point.
This module initializes and runs the Flask application.
"""

from app import create_app, db
from flask_migrate import upgrade

# Create the Flask application instance
app = create_app()

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    try:
        # Migrate database to latest revision
        upgrade()
        app.logger.info("Database migration completed successfully")
    except Exception as e:
        app.logger.error(f"Error during deployment: {str(e)}")
        raise

if __name__ == '__main__':
    # Run the application in debug mode for development
    app.run(debug=True)
