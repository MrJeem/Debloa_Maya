import math
import maya.cmds as cmds
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui
from PySide2 import QtWidgets, QtGui, QtCore

RECOMMENDED_UNLOAD = ['AbcExport', 'AbcImport', 'Boss', 'GamePipeline', 'MASH', 'MayaMuscle', 'bifmeshio',
                      'bifrostGraph', 'bifrostshellnode', 'gameFbxExporter',
                      'ATFPlugin', 'hairPhysicalShader', 'lookdevKit', 'mayaCharacterization', 'mayaHIK',
                      'mayaUsdPlugin', 'mayaVnnPlugin', 'modelingToolkit',
                      'mtoa', 'sceneAssembly', 'shaderFXPlugin', 'stereoCamera', 'svgGileTranslator', 'xgenToolkit',
                      'bifrostvisplugin']


class PluginUnloadWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):

        # Let's delete the earlier window first
        if cmds.window('pluginUnloadWin', exists=True):
            cmds.deleteUI('pluginUnloadWin', window=True)

        super(PluginUnloadWindow, self).__init__(parent)

        # Main window and layout
        self.setWindowTitle('De-bloat Maya')
        self.setObjectName('pluginUnloadWin')
        layout = QtWidgets.QVBoxLayout()

        # List all currently loaded plugins
        self.plugin_checkboxes = {}
        all_plugins = sorted(cmds.pluginInfo(query=True, listPlugins=True))

        # Define the number of columns based on the number of plugins
        num_columns = max(1, int(math.sqrt(len(all_plugins)) / 2))

        grid_layout = QtWidgets.QGridLayout()
        for index, plugin in enumerate(all_plugins):
            # Make some rows and columns
            row = index // num_columns
            col = index % num_columns

            # Ticking recommended plugins already
            is_checked = plugin in RECOMMENDED_UNLOAD
            checkbox = QtWidgets.QCheckBox(plugin)
            checkbox.setChecked(is_checked)

            # Add the widget to the main layout
            grid_layout.addWidget(checkbox, row, col)

            # Add to the dictionary to be used later
            self.plugin_checkboxes[plugin] = checkbox

        layout.addLayout(grid_layout)

        # The button
        unload_button = QtWidgets.QPushButton("Unload")
        unload_button.clicked.connect(self.unload_plugins)

        layout.addWidget(unload_button)

        self.setLayout(layout)

    # Main function to unload and disable autoload
    def unload_plugins(self):
        exceptions = {}
        for plugin, checkbox in self.plugin_checkboxes.items():
            if checkbox.isChecked():
                # Unload the plugin
                try:
                    cmds.unloadPlugin(plugin)
                except Exception as e:
                    exceptions[plugin] = e
                # Stop the autoload
                cmds.pluginInfo(plugin, edit=True, autoload=False)

        # Present all the not unloaded plugins in the script editor
        for plugin, exception in exceptions.items():
            print('================================')
            print("'Couldn't unload {}".format(plugin))
            print("StackTrace:")
            print(str(exception).strip())
            print('================================')
            print('\n')

        # Inform the user nicely about the unloaded plugins
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Plugins")
        msg_box.setText("Unloading process done. Please check script editor for more details.")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec_()
        show_window()


def show_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    main_window = wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

    window_instance = PluginUnloadWindow(parent=main_window)
    window_instance.show()
    return window_instance


if __name__ == '__main__':
    show_window()
