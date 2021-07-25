from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "NnuUKdVF71sppI6cia7XXf386_AbYUnnXnmdaOW_PRy_sGawZXfScC_DoGNAO0r6H4WgNwGGeCnaXxevUapfyw"

from src import routes