import logging
# PyQt needs to be imported like this because for whatever reason they decided not to include a __all__ = [...]
import PyQt5.QtWidgets as QtWidgets

from core import api_handler
from config import config
from parsers import supported_parsers

# Colour Codes
COLOUR_GREEN_LIGHT = "#D9F7BE"
COLOUR_RED_LIGHT = "#FFCCC7"


class ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.debug("GUI: Setting up ConfigDialog")

        # Widgets
        self._client_id_label = QtWidgets.QLabel("Client ID")
        self._client_id = QtWidgets.QLineEdit()
        self._client_secret_label = QtWidgets.QLabel("Client Secret")
        self._client_secret = QtWidgets.QLineEdit()
        self._username_label = QtWidgets.QLabel("Username")
        self._username = QtWidgets.QLineEdit()
        self._password_label = QtWidgets.QLabel("Password")
        self._password = QtWidgets.QLineEdit()
        self._password.setEchoMode(QtWidgets.QLineEdit.Password)
        self._base_url_label = QtWidgets.QLabel("Base URL")
        self._base_url = QtWidgets.QLineEdit()
        self._parser_label = QtWidgets.QLabel("Parser")
        self._parser = QtWidgets.QComboBox()
        self._parser.addItems(supported_parsers)

        self._btn_check_settings = QtWidgets.QPushButton("Save and Test Settings")
        self._settings_status = QtWidgets.QLineEdit()
        self._settings_status.setReadOnly(True)
        self._settings_status.setEnabled(False)
        self._settings_status.setStyleSheet("color: black")
        self._btn_accept = QtWidgets.QPushButton("Accept")
        self._btn_cancel = QtWidgets.QPushButton("Cancel")

        # connections
        self._btn_check_settings.clicked.connect(self._check_connection_to_irida)
        self._btn_accept.clicked.connect(self._accept_and_exit)
        self._btn_cancel.clicked.connect(self._cancel_and_exit)

        # Set Layout and Geometry
        self.setLayout(self._layout())
        self.setGeometry(0, 0, 600, 300)

        # Init settings
        self._get_settings_from_file()
        self._contact_irida()

    def _layout(self):
        """
        Layout widgets
        :return: QtWidgets.QVBoxLayout()
        """
        # base layout
        layout = QtWidgets.QVBoxLayout()
        # Client ID
        client_id_layout = QtWidgets.QHBoxLayout()
        client_id_layout.addWidget(self._client_id_label)
        client_id_layout.addWidget(self._client_id)
        layout.addLayout(client_id_layout)
        # Client Secret
        client_secret_layout = QtWidgets.QHBoxLayout()
        client_secret_layout.addWidget(self._client_secret_label)
        client_secret_layout.addWidget(self._client_secret)
        layout.addLayout(client_secret_layout)
        # Username
        username_layout = QtWidgets.QHBoxLayout()
        username_layout.addWidget(self._username_label)
        username_layout.addWidget(self._username)
        layout.addLayout(username_layout)
        # Password
        password_layout = QtWidgets.QHBoxLayout()
        password_layout.addWidget(self._password_label)
        password_layout.addWidget(self._password)
        layout.addLayout(password_layout)
        # Base URL
        base_url_layout = QtWidgets.QHBoxLayout()
        base_url_layout.addWidget(self._base_url_label)
        base_url_layout.addWidget(self._base_url)
        layout.addLayout(base_url_layout)
        # Parser
        parser_layout = QtWidgets.QHBoxLayout()
        parser_layout.addWidget(self._parser_label)
        parser_layout.addWidget(self._parser)
        layout.addLayout(parser_layout)
        # Buttons
        status_layout = QtWidgets.QHBoxLayout()
        status_layout.addWidget(self._btn_check_settings)
        status_layout.addWidget(self._settings_status)
        layout.addLayout(status_layout)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self._btn_accept)
        button_layout.addWidget(self._btn_cancel)
        layout.addLayout(button_layout)

        return layout

    def _accept_and_exit(self):
        """
        Writes the settings to file and then closes
        :return:
        """
        self._write_settings_to_file()
        self._contact_irida()
        self.close()

    def _cancel_and_exit(self):
        """
        closes this widget
        :return:
        """
        self.close()

    def _get_settings_from_file(self):
        """
        Loads the config settings from file and fills the widgets
        :return:
        """
        config.setup()
        self._client_id.setText(config.read_config_option('client_id'))
        self._client_secret.setText(config.read_config_option('client_secret'))
        self._username.setText(config.read_config_option('username'))
        self._password.setText(config.read_config_option('password'))
        self._base_url.setText(config.read_config_option('base_url'))
        index = self._parser.findText(config.read_config_option('parser'))
        self._parser.setCurrentIndex(index)

    def _write_settings_to_file(self):
        """
        Writes the settings in the config boxes to file
        :return:
        """
        config.set_config_options(client_id=self._client_id.text(),
                                  client_secret=self._client_secret.text(),
                                  username=self._username.text(),
                                  password=self._password.text(),
                                  base_url=self._base_url.text(),
                                  parser=self._parser.currentText())
        config.write_config_options_to_file()

    def _contact_irida(self):
        """
        Attempts to connect to IRIDA
        Sets the style and text of the status widget to green/red to indicate connected/error
        :return:
        """
        try:
            api_handler.initialize_api_from_config()
            self._settings_status.setText("Connection OK")
            self._settings_status.setStyleSheet("background-color: {}; color: black;".format(COLOUR_GREEN_LIGHT))
            logging.info("Successfully connected to IRIDA")
        except Exception:
            self._settings_status.setText("ERROR!")
            self._settings_status.setStyleSheet("background-color: {}; color: black;".format(COLOUR_RED_LIGHT))
            logging.info("Error occurred while trying to connect to IRIDA")

    def _check_connection_to_irida(self):
        """
        Writes the settings in the boxes to the config file, and then tries to connect to IRIDA
        :return:
        """
        self._write_settings_to_file()
        self._contact_irida()

    def center_window(self):
        """
        sets the dialog position to the center of the parent
        :return:
        """
        qt_rectangle = self.frameGeometry()
        parent_geo = self.parent().frameGeometry().center()
        qt_rectangle.moveCenter(parent_geo)
        self.move(qt_rectangle.topLeft())
