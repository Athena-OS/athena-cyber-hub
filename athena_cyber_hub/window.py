# window.py
#
# Copyright: 2023 Antonio Voza
#            2023 Mirko Brombin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-only

import logging
import subprocess
from gi.repository import Adw
from gi.repository import Gtk, GLib, GObject
from gettext import gettext as _

from athena_cyber_hub.program import AthenaAchProgram
from athena_cyber_hub.container import AthenaAchContainer
from athena_cyber_hub.backends.ach import Ach
from athena_cyber_hub.dialog_installation import AthenaDialogInstallation
from athena_cyber_hub.run_async import RunAsync


logger = logging.getLogger("Athena")


@Gtk.Template(resource_path='/org/athenaos/CyberHub/gtk/window.ui')
class AthenaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AthenaWindow'
    __gsignals__ = {
        "installation-finished": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    toasts = Gtk.Template.Child()
    page_ach = Gtk.Template.Child()
    page_csp = Gtk.Template.Child()
    page_cl = Gtk.Template.Child()
    group_cve_containers = Gtk.Template.Child()
    group_owasp_containers = Gtk.Template.Child()
    group_additional_containers = Gtk.Template.Child()
    group_custom_containers = Gtk.Template.Child()
    group_platforms = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__selected_default = None
        self.ach = Ach()
        self.__build_ui()

    def __build_ui(self):
        self.__setup_ach()
        self.__setup_csp()
        self.__setup_cl()

    # region Ach
    def __setup_ach(self):
        if not self.ach.supported:
            self.page_ach.set_visible(False)
            return
            
        for container in self.ach.containers:
            _row = AthenaAchContainer(self, container)
            self.group_cve_containers.add(_row)

        for container in self.ach.owasp_containers:
            _row = AthenaAchContainer(self, container)
            self.group_owasp_containers.add(_row)

        for container in self.ach.additional_containers:
            _row = AthenaAchContainer(self, container)
            self.group_additional_containers.add(_row)

    # endregion

    # region Csp
    def __setup_csp(self):
        if not self.ach.supported:
            self.page_csp.set_visible(False)
            return
            
        for platform in self.ach.platforms:
            _row = AthenaAchContainer(self, platform) #AthenaAchContainer because platforms follow the same rules of Containers
            self.group_platforms.add(_row)

    # endregion

    # region Cl
    def __setup_cl(self):
        if not self.ach.supported:
            self.page_cl.set_visible(False)
            return
            
        for container in self.ach.custom_containers:
            _row = AthenaAchContainer(self, container)
            self.group_custom_containers.add(_row)

    # endregion

    def toast(self, message, timeout=2):
        toast = Adw.Toast.new(message)
        toast.props.timeout = timeout
        self.toasts.add_toast(toast)