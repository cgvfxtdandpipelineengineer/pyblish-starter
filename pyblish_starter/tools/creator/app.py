import sys
from . import new_combine #my_code
from ...vendor.Qt import QtWidgets, QtCore
from ... import pipeline
from .. import lib
from PySide2.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QComboBox, QWidget, QPushButton, QDialog, QGridLayout

self = sys.modules[__name__]
self._window = None


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Asset Creator")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        lists = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        container = QtWidgets.QWidget()

        listing = QtWidgets.QListWidget()
        name = QtWidgets.QLineEdit()

        layout = QtWidgets.QVBoxLayout(container)
        layout.addWidget(QtWidgets.QLabel("Family"))
        layout.addWidget(listing)
        layout.addWidget(QtWidgets.QLabel("Name"))
        layout.addWidget(name)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()

        autoclose_chk = QtWidgets.QCheckBox("Close after creation")
        autoclose_chk.setCheckState(QtCore.Qt.Checked)

        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(autoclose_chk, 1, 0)

        layout = QtWidgets.QHBoxLayout(lists)
        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(body)
        layout.addWidget(lists)
        layout.addWidget(options, 0, QtCore.Qt.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)

        create_btn = QtWidgets.QPushButton("Create")
        error_msg = QtWidgets.QLabel()
        error_msg.hide()

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(create_btn)
        layout.addWidget(error_msg)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        names = {
            create_btn: "Create Button",
            listing: "Listing",
            # useselection_chk: "Use Selection Checkbox",
            autoclose_chk: "Autoclose Checkbox",
            name: "Name",
            error_msg: "Error Message",
        }

        for widget, name_ in names.items():
            widget.setObjectName(name_)

        create_btn.clicked.connect(self.on_create)
        name.returnPressed.connect(self.on_create)
        name.textChanged.connect(self.on_data_changed)
        listing.currentItemChanged.connect(self.on_data_changed)
        listing.itemDoubleClicked.connect(self.on_item_double_clicked) #my code

        # Defaults
        self.resize(220, 250)
        name.setFocus()
        create_btn.setEnabled(False)

    #my_code
    def on_item_double_clicked(self, item):
        name = item.text()
        if name == "starter.playblast":
            print("HAHAHAHAHHAHA")
            self.close()

            my_window = QDialog(self)
            my_window.setFixedSize(200, 150)

            my_layout = QVBoxLayout()
            my_comboBox = QComboBox()
            camera_options = new_combine.get_cameras()
            my_comboBox.addItems(camera_options)

            playblast_button = QPushButton("playblast specific camera")
            playblast_button.setStyleSheet("background-color: white; color:black")

            combine_button = QPushButton("combine all cameras")
            combine_button.setStyleSheet("background-color: white; color:black")
            combine_button.clicked.connect(self._combine_playblasts)
            
            my_layout.addWidget(my_comboBox)
            my_layout.setContentsMargins(0, 0, 0, 0)

            my_layout.addWidget(playblast_button)
            my_layout.setContentsMargins(5, 5, 5, 5)
           
            my_layout.addWidget(combine_button)
            my_layout.setSpacing(20)
            my_window.setLayout(my_layout)
            my_window.show()

    def _combine_playblasts(self):

        all_cameras = new_combine.get_cameras()
        output_directory = new_combine.get_output_directory()

        list_of_videos = new_combine.capturing_videos(all_cameras, output_directory)

        output_file = new_combine.get_output_file("combined_video_test1.mov")
        all_paths = new_combine.get_all_paths_file("my_videos.txt")

        new_combine.combine_videos(list_of_videos, output_file, all_paths)

    def on_data_changed(self, *args):
        button = self.findChild(QtWidgets.QPushButton, "Create Button")
        name = self.findChild(QtWidgets.QWidget, "Name")
        item = self.findChild(QtWidgets.QWidget, "Listing").currentItem()

        button.setEnabled(
            name.text().strip() != "" and
            item.data(QtCore.Qt.ItemIsEnabled)
        )

    def keyPressEvent(self, event):
        """Custom keyPressEvent.
        
        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands
        whilst trying to name an instance.

        """

    def refresh(self, families):
        listing = self.findChild(QtWidgets.QWidget, "Listing")

        has_families = False

        for family in families:
            item = QtWidgets.QListWidgetItem(family["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(QtCore.Qt.UserRole + 2, family.get("help"))
            listing.addItem(item)

            has_families = True

        if not has_families:
            item = QtWidgets.QListWidgetItem("No registered families")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            listing.addItem(item)

        listing.setCurrentItem(listing.item(0))

    def on_create(self):
        listing = self.findChild(QtWidgets.QWidget, "Listing")
        autoclose_chk = self.findChild(QtWidgets.QWidget,
                                       "Autoclose Checkbox")
        error_msg = self.findChild(QtWidgets.QWidget, "Error Message")

        item = listing.currentItem()

        if item is not None:
            family = item.text()
            name = self.findChild(QtWidgets.QWidget, "Name").text()

            try:
                pipeline.registered_host().create(name, family)

            except NameError as e:
                error_msg.setText(str(e))
                error_msg.show()
                raise

            except (TypeError, RuntimeError, KeyError, AssertionError) as e:
                error_msg.setText("Program error: %s" % str(e))
                error_msg.show()
                raise

        if autoclose_chk.checkState():
            self.close()


def show(debug=False):
    """Display asset creator GUI

    Arguments:
        creator (func, optional): Callable function, passed `name`,
            `family` and `use_selection`, defaults to `creator`
            defined in :mod:`pipeline`
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    families = pipeline.registered_families()

    if self._window:
        self._window.close()
        del(self._window)

    if debug:
        families.append({"name": "debug.model"})
        families.append({"name": "debug.rig"})
        families.append({"name": "debug.animation"})
        families.append({"name": "debug.playblast"})

    try:
        widgets = QtWidgets.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets["MayaWindow"]
    except KeyError:
        parent = None

    with lib.application():
        window = Window(parent)
        window.refresh(families)
        window.show()

        self._window = window
