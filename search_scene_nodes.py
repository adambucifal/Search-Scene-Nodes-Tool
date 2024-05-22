try:
	from PySide2 import QtCore, QtWidgets
	from shiboken2 import wrapInstance

except ModuleNotFoundError:
	from PySide6 import QtCore, QtWidgets
	from shiboken6 import wrapInstance


import maya.OpenMayaUI as omui
import maya.cmds as cmds
import sys


def maya_main_window() -> QtWidgets.QWidget:
	"""
	Returns maya's mainwindow
	
	:return: QtWidgets.QWidget
	"""
	return wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)


class SearchSceneNodes(QtWidgets.QDialog):
	
	NO_NODETYPE: str = ""
	last_sel_node_type: str = NO_NODETYPE
	
	ALL_NODETYPES: list[str] = cmds.allNodeTypes()
	NODETYPES_DISPLAY: list[str] = [last_sel_node_type] + ALL_NODETYPES
	
	ui_instance = None
	
	@classmethod
	def show_ui(cls) -> None:
		"""
		Creates the UI and stores the instance so if closed and reopened, 
			user inputs are maintained
		
		:return: None
		"""
		if not cls.ui_instance:
			cls.ui_instance = SearchSceneNodes()
		
		if cls.ui_instance.isHidden():
			cls.ui_instance.show()
		
		else:
			cls.ui_instance.raise_()
			cls.ui_instance.activateWindow()
	
	
	def __init__(self) -> None:
		"""
		Initialize the inherited class and create the ui

		:return: None
		"""
		super().__init__(maya_main_window())
		
		self.setWindowTitle("Search Scene Nodes")
		self.setMinimumSize(300, 200)
		
		if sys.platform == "darwin":
			self.setWindowFlag(QtCore.Qt.Tool, True)
		
		self.scene_nodes = cmds.ls()
		
		self.create_widgets()
		self.create_connections()
		self.create_layout()
		
		self.update_display_nodes()
	

	def create_widgets(self) -> None:
		"""
		Creates QWidgets
		
		:return: None
		"""
		self.search_le = QtWidgets.QLineEdit()
		
		# Filter by node type combo box
		self.nodetype_cb = QtWidgets.QComboBox()
		self.nodetype_cb.addItems(self.NODETYPES_DISPLAY)
		self.nodetype_cb.setEditable(True)
		self.nodetype_cb.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
		self.nodetype_cb.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
		
		self.clear_nodetype_btn = QtWidgets.QPushButton("Clear Node Type")
		self.reload_nodes_btn = QtWidgets.QPushButton("Reload Scene Nodes")
		
		self.display_nodes_lw = QtWidgets.QListWidget()
		self.display_nodes_lw.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
	
	
	def create_layout(self) -> None:
		"""
		Creates the layout for the ui
		
		:return: None
		"""
		grid_layout = QtWidgets.QGridLayout()
		grid_layout.addWidget(self.nodetype_cb, 0, 0)
		grid_layout.addWidget(self.clear_nodetype_btn, 0, 1)
		grid_layout.addWidget(self.reload_nodes_btn, 0, 2)
		
		form_layout = QtWidgets.QFormLayout()
		form_layout.addRow("Filter node type", grid_layout)
		form_layout.addRow("Search scene", self.search_le)
		form_layout.addRow(self.display_nodes_lw)
		
		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.addLayout(form_layout)
	
	
	def create_connections(self) -> None:
		"""
		Creates connections between the widgets and functions
		
		:return: None
		"""
		self.search_le.textChanged.connect(self.update_display_nodes)
		self.display_nodes_lw.itemSelectionChanged.connect(self.item_selection_changed)
		self.nodetype_cb.currentIndexChanged.connect(self.update_node_type)
		self.clear_nodetype_btn.clicked.connect(
			lambda: search_scene_nodes_win.nodetype_cb.setCurrentIndex(0)
		)
		self.reload_nodes_btn.clicked.connect(self.reload_scene_nodes)
	
	
	# Utility methods
	def update_node_type(self, index: int) -> None:
		"""
		Applies the filter node type from the ui and re assigns self.scene_nodes
		
		:param index: int - arg passed from the QComboBox widget of the selected item's index
		
		:return: None
		"""
		current_sel_node_type = self.nodetype_cb.itemText(index)
		self.filter_node_type(current_sel_node_type)

	
	def filter_node_type(self, node_type: str) -> None:
		"""
		Apply node type filter to all scene nodes
		
		:param node_type: str - any valid maya node type
		
		:return: None
		"""
		if node_type == self.nodetype_cb.itemText(0):
			self.scene_nodes = cmds.ls()
				
		else:
			self.scene_nodes = cmds.ls(type=node_type)
		
		self.update_display_nodes()
		self.last_sel_node_type = node_type
		
	
	def reload_scene_nodes(self):
		"""
		Reload all scene nodes and apply the filters
		
		:return: None
		"""
		node_type = self.nodetype_cb.currentText()
		self.filter_node_type(node_type)
	
	
	def update_display_nodes(self) -> None:
		"""
		Updates the QListWidget in the ui with the filtered nodes
		
		:return: None
		"""
		filter_string = self.search_le.text()

		self.display_nodes_lw.clear()
		self.display_nodes_lw.addItems([
			node for node in self.scene_nodes if filter_string.lower() in node.lower()
		])
	
	
	def item_selection_changed(self) -> None:
		"""
		Selects the selected items in the ui
		
		:return: None
		"""
		cmds.select(
			[
				item.text() 
				for item in self.display_nodes_lw.selectedItems() 
				if cmds.objExists(item.text())
			]
		)

if __name__ == "__main__":
	
	try:
		search_scene_nodes_win.close()
		search_scene_nodes_win.deleteLater()
	
	except:
		pass
		
	search_scene_nodes_win = SearchSceneNodes()
	search_scene_nodes_win.show()
	