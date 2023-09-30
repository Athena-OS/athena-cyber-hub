# ach.py
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
# SPDX-License-Identifier: GPL-3.0-only#

import os
import re
import logging
import subprocess
import shutil
import toml
from pathlib import Path
from enum import Enum
from glob import glob
from gettext import gettext as _

logger = logging.getLogger("Athena::Ach")


class Ach:

    def __init__(self):
        self.__binary = "/usr/bin/docker"
        stat = subprocess.call(["systemctl", "is-active", "--quiet", "docker"])
        #if(stat != 0):  # if 0 (active), otherwise (stopped)"
        #    self.docker_start = subprocess.run(["pkexec", "systemctl", "start", "docker"], capture_output=True)
        #else:
        #    print("Docker daemon already running.")
        #self.pulled_containers = subprocess.run(["pkexec", self.__binary, "ps", "-a", "--format", "'{{.Image}}'"], capture_output=True)
        self.pulled_containers = subprocess.run(["pkexec", "bash", "-c", "systemctl start docker; docker ps -a --format '{{.Image}}'"], capture_output=True)


    config_directory = os.environ['HOME']+"/.config/athena-cyber-hub"
    # Check if the directory exists
    if not os.path.exists(config_directory):
        # If it doesn't exist, create it
        os.makedirs(config_directory)
        shutil.copy2('/usr/share/athena-cyber-hub/cyberlab/cyberlab.toml', config_directory)

    data = toml.load("/usr/share/athena-cyber-hub/vulhub/environments.toml")

#######################################################
#######################################################
###                 VULHUB CONTAINERS               ###
#######################################################
#######################################################

    __managed_containers = {}
    __additional_containers = {}

    for item in data['environment']:
        item['name'] = (item['name']).replace('<',"&lt;") # double-quotes with &lt; are important. Solving GTK markup issue due to < character in 'name', for example: Failed to set text 'Celery <4.0 Redis Unauthorized Access and Pickle Deserialization' from markup due to error parsing markup: Error on line 1 char 27: Odd character “U”, expected a “=” after attribute name “Redis” of element “4.0”
        item['name'] = (item['name']).replace('>',"&gt;")
        
        if item['cve']:
            img_name = (item['cve'][0]+"-"+re.findall('(.+)(?=/)', item['path'])[0]).lower()
            alias = img_name
            __managed_containers[alias] = {
                _("Name"): _(item['name']),
                _("App"): _(item['app']),
                _("ShellCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/vulhub/{item['path']}/docker-compose.yml up",
                _("InitCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/vulhub/{item['path']}/docker-compose.yml up",
                _("DeleteCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/vulhub/{item['path']}/docker-compose.yml down -v",
                _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/vulhub/{item['path']}/README.md",
            }
        else:
            img_name = (subprocess.run(["grep", "-h", "-m", "1", "-oP", '(?<=image: ).*|(?<=FROM ).*', "/usr/share/athena-cyber-hub/vulhub/"+item['path']+"/docker-compose.yml", "/usr/share/athena-cyber-hub/vulhub/"+item['path']+"/Dockerfile"], capture_output=True, text=True)).stdout.replace(' ','').replace('\n','') # Getting only the first occurrence of "image:" because we need only the first one for checking if the container is running or not, also for cases where docker-compose.yml are more image names

            if os.path.isfile("/usr/share/athena-cyber-hub/vulhub/"+item['path']+"/docker-compose.yml") and os.path.isfile("/usr/share/athena-cyber-hub/vulhub/"+item['path']+"/Dockerfile"):
                img_name = (subprocess.run(["grep", "-h", "-m", "1", "-oP", '(?<=FROM ).*', "/usr/share/athena-cyber-hub/vulhub/"+item["path"]+"/Dockerfile"], capture_output=True, text=True)).stdout.replace(' ','').replace('\n','') # If the folder has both docker-compose.yml and Dockerfile, take the image name from Dockerfile

            alias = img_name
            __additional_containers[alias] = {
                _("Name"): _(item['name']),
                _("App"): _(item['app']),
                _("ShellCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/vulhub/{item['path']}/docker-compose.yml up",
                _("InitCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/vulhub/{item['path']}/docker-compose.yml up",
                _("DeleteCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/vulhub/{item['path']}/docker-compose.yml down -v",
                _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/vulhub/{item['path']}/README.md",
            }
        

#######################################################
#######################################################
###                     OWASP                       ###
#######################################################
#######################################################

    __owasp_containers = {
        "juice-shop":{ # This alias will be used for checking if the container has been pulled or not. Look __get_containers() and its alias variable
            _("Name"): _("OWASP Juice Shop"),
            _("ShellCmd"): f"kgx -e \"sudo docker start juice-shop; echo 'Container already in your system. Visit localhost:3000 by the browser.'\"",
            _("InitCmd"): f"kgx -e sudo docker run --name juice-shop -p 3000:3000 bkimminich/juice-shop",
            _("DeleteCmd"): "kgx -e \"sudo docker rm $(sudo docker stop $(sudo docker ps -a --filter ancestor=bkimminich/juice-shop --format={{.ID}})); echo 'Container removed from your system.'\"", # Don't use f" at the beginning otherwise {{.ID}} will be used as a Python variable
            _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/owasp/juice-shop/README.md",
        },
        "bwapp":{ # This alias will be used for checking if the container has been pulled or not. Look __get_containers() and its alias variable
            _("Name"): _("OWASP bWAPP (Buggy Web Application)"),
            _("ShellCmd"): f"kgx -e \"sudo docker start bwapp; echo 'Container already in your system. Visit localhost:80 by the browser.'\"",
            _("InitCmd"): f"kgx -e sudo docker run --name bwapp -p 80:80 raesene/bwapp",
            _("DeleteCmd"): "kgx -e \"sudo docker rm $(sudo docker stop $(sudo docker ps -a --filter ancestor=raesene/bwapp --format={{.ID}})); echo 'Container removed from your system.'\"", # Don't use f" at the beginning otherwise {{.ID}} will be used as a Python variable
            _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/owasp/bwapp/README.md",
        },
        "dvga":{ # This alias will be used for checking if the container has been pulled or not. Look __get_containers() and its alias variable
            _("Name"): _("OWASP DVGA (Damn Vulnerable GraphQL Application)"),
            _("ShellCmd"): f"kgx -e \"sudo docker start dvga; echo 'Container already in your system. Visit localhost:5013 by the browser.'\"",
            _("InitCmd"): f"kgx -e sudo docker run --name dvga -t -p 5013:5013 -e WEB_HOST=0.0.0.0 dolevf/dvga",
            _("DeleteCmd"): "kgx -e \"sudo docker rm $(sudo docker stop $(sudo docker ps -a --filter ancestor=dolevf/dvga --format={{.ID}})); echo 'Container removed from your system.'\"", # Don't use f" at the beginning otherwise {{.ID}} will be used as a Python variable
            _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/owasp/dvga/README.md",
        },
        "dvna":{ # This alias will be used for checking if the container has been pulled or not. Look __get_containers() and its alias variable
            _("Name"): _("OWASP DVNA (Damn Vulnerable NodeJS Application)"),
            _("ShellCmd"): f"kgx -e \"sudo docker start dvna; echo 'Container already in your system. Visit localhost:9090 by the browser.'\"",
            _("InitCmd"): f"kgx -e sudo docker run --name dvna -p 9090:9090 appsecco/dvna:sqlite",
            _("DeleteCmd"): "kgx -e \"sudo docker rm $(sudo docker stop $(sudo docker ps -a --filter ancestor=appsecco/dvna --format={{.ID}})); echo 'Container removed from your system.'\"", # Don't use f" at the beginning otherwise {{.ID}} will be used as a Python variable
            _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/owasp/dvna/README.md",
        },
        #"dvjs":{ # This alias will be used for checking if the container has been pulled or not. Look __get_containers() and its alias variable
        #    _("Name"): _("OWASP DVJS (Damn Vulnerable Javascript SCA)"),
        #    _("ShellCmd"): f"kgx -e \"sudo docker start dvjs; echo 'Container already in your system. Visit localhost:3000 and localhost:3001 by the browser.'\"",
        #    _("InitCmd"): f"kgx -e sudo docker run --name dvjs -p 3000:3000 -p 3001:3001 -it ghcr.io/lunasec-io/damn-vulnerable-js-sca",
        #    _("DeleteCmd"): "kgx -e \"sudo docker rm $(sudo docker stop $(sudo docker ps -a --filter ancestor=lunasec-io/damn-vulnerable-js-sca --format={{.ID}})); echo 'Container removed from your system.'\"", # Don't use f" at the beginning otherwise {{.ID}} will be used as a Python variable
        #    _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/owasp/dvjs/README.md",
        #},
        "webgoat":{ # This alias will be used for checking if the container has been pulled or not. Look __get_containers() and its alias variable
            _("Name"): _("OWASP WebGoat"),
            _("ShellCmd"): f"kgx -e \"sudo docker start webgoat; echo 'Container already in your system. Visit localhost:8080 for WebGoat and localhost:9090 for WebWolf by the browser.'\"",
            _("InitCmd"): f"kgx -e sudo docker run --name webgoat -it -p 127.0.0.1:8080:8080 -p 127.0.0.1:9090:9090 webgoat/webgoat",
            _("DeleteCmd"): "kgx -e \"sudo docker rm $(sudo docker stop $(sudo docker ps -a --filter ancestor=webgoat/webgoat --format={{.ID}})); echo 'Container removed from your system.'\"", # Don't use f" at the beginning otherwise {{.ID}} will be used as a Python variable
            _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/owasp/webgoat/README.md",
        },
        "wrongsecrets":{ # This alias will be used for checking if the container has been pulled or not. Look __get_containers() and its alias variable
            _("Name"): _("OWASP WrongSecrets"),
            _("ShellCmd"): f"kgx -e \"sudo docker start wrongsecrets; echo 'Container already in your system. Visit localhost:8080 by the browser.'\"",
            _("InitCmd"): f"kgx -e sudo docker run --name wrongsecrets -p 8080:8080 jeroenwillemsen/wrongsecrets:latest-no-vault",
            _("DeleteCmd"): "kgx -e \"sudo docker rm $(sudo docker stop $(sudo docker ps -a --filter ancestor=jeroenwillemsen/wrongsecrets:latest-no-vault --format={{.ID}})); echo 'Container removed from your system.'\"", # Don't use f" at the beginning otherwise {{.ID}} will be used as a Python variable
            _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/owasp/wrongsecrets/README.md",
        },
        "xvwa":{ # This alias will be used for checking if the container has been pulled or not. Look __get_containers() and its alias variable
            _("Name"): _("OWASP XVWA (Xtreme Vulnerable Web Application)"),
            _("ShellCmd"): f"kgx -e \"sudo docker start xvwa; echo 'Container already in your system. Visit localhost:80 by the browser.'\"",
            _("InitCmd"): f"kgx -e sudo docker run --name xvwa -p 80:80 tuxotron/xvwa",
            _("DeleteCmd"): "kgx -e \"sudo docker rm $(sudo docker stop $(sudo docker ps -a --filter ancestor=tuxotron/xvwa --format={{.ID}})); echo 'Container removed from your system.'\"", # Don't use f" at the beginning otherwise {{.ID}} will be used as a Python variable
            _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/owasp/xvwa/README.md",
        }
    }

#######################################################
#######################################################
###                CUSTOM CONTAINERS                ###
#######################################################
#######################################################

    data = toml.load(config_directory+"/cyberlab.toml")
    __custom_containers = {}

    for item in data['environment']:
        item['name'] = (item['name']).replace('<',"&lt;") # double-quotes with &lt; are important. Solving GTK markup issue due to < character in 'name', for example: Failed to set text 'Celery <4.0 Redis Unauthorized Access and Pickle Deserialization' from markup due to error parsing markup: Error on line 1 char 27: Odd character “U”, expected a “=” after attribute name “Redis” of element “4.0”
        item['name'] = (item['name']).replace('>',"&gt;")

        alias = (item['id'])
        __custom_containers[alias] = {
            _("Name"): _(item['name']),
            _("ID"): _(item['id']),
            _("ShellCmd"): f"kgx -e sudo docker compose -f {item['path_docker']} up",
            _("InitCmd"): f"kgx -e sudo docker compose -f {item['path_docker']} up",
            _("DeleteCmd"): f"kgx -e \"sudo docker compose -f {item['path_docker']} down -v; echo 'Container removed from your system.'\"",
            _("ReadCmd"): f"marktext {item['path_readme']}",
        }

#######################################################
#######################################################
###               PLATFORM CONTAINERS               ###
#######################################################
#######################################################

    __managed_platforms = {
        "defectdojo":{ # This alias will be used for checking if the container has been pulled or not. Look __get_platforms() and its alias variable
            _("Name"): _("DefectDojo"),
            _("ShellCmd"): f"kgx -e \"cd /usr/share/athena-cyber-hub/platforms/defectdojo; sudo /usr/share/athena-cyber-hub/platforms/defectdojo/dc-up.sh\"",
            _("InitCmd"): f"kgx -e \"cd /usr/share/athena-cyber-hub/platforms/defectdojo; sudo /usr/share/athena-cyber-hub/platforms/defectdojo/dc-up.sh\"",
            _("DeleteCmd"): f"kgx -e \"cd /usr/share/athena-cyber-hub/platforms/defectdojo; sudo /usr/share/athena-cyber-hub/platforms/defectdojo/dc-down.sh\"",
            _("ReadCmd"): f"marktext /usr/share/athena-cyber-hub/platforms/defectdojo/README.md",
        },
        "greenbone": {
            _("Name"): _("Greenbone OpenVAS"),
            _("ShellCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/platforms/greenbone/docker-compose.yml -p greenbone-community-edition up",
            _("InitCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/platforms/greenbone/docker-compose.yml -p greenbone-community-edition up",
            _("DeleteCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/platforms/greenbone/docker-compose.yml -p greenbone-community-edition down -v",
            _("ReadCmd"): f"xdg-open https://greenbone.github.io/docs/latest",
        },
        "wazuh": {
            _("Name"): _("Wazuh"),
            _("ShellCmd"): f"kgx -e \"sudo sysctl -w vm.max_map_count=262144; sudo docker-compose -f generate-indexer-certs.yml run --rm generator; sudo docker compose -f /usr/share/athena-cyber-hub/platforms/wazuh/docker-compose.yml up\"",
            _("InitCmd"): f"kgx -e \"sudo sysctl -w vm.max_map_count=262144; sudo docker-compose -f generate-indexer-certs.yml run --rm generator; sudo docker compose -f /usr/share/athena-cyber-hub/platforms/wazuh/docker-compose.yml up\"",
            _("DeleteCmd"): f"kgx -e sudo docker compose -f /usr/share/athena-cyber-hub/platforms/wazuh/docker-compose.yml down -v",
            _("ReadCmd"): f"xdg-open https://documentation.wazuh.com/current/index.html",
        }
    }

#######################################################
#######################################################   

    @property
    def supported(self) -> bool:
        if self.__binary is None:
            logger.info(_("Docker binary not found"))
            return False

        return True

    @property
    def containers(self) -> list:
        return self.__get_containers()

    @property
    def owasp_containers(self) -> list:
        return self.__get_owasp_containers()

    @property
    def additional_containers(self) -> list:
        return self.__get_additional_containers()

    @property
    def custom_containers(self) -> list:
        return self.__get_custom_containers()

    @property
    def platforms(self) -> list:
        return self.__get_platforms()


### CVE CONTAINERS

    def __get_containers(self) -> list:
        if not self.supported:
            return []

        res = self.pulled_containers
        if res.returncode != 0:
            logger.error(_("Unable to get containers. Check if docker daemon is running."))
            return []
            
        containers = []
        for alias, container in self.__managed_containers.items():
            _container = {
                "Name": container["Name"],
                "Status": 1,
                "Alias": (re.findall('cve-\d{4}-\d{4,7}',alias)[0]).replace('cve','CVE'), # It will show CVE as subtitle on the GTK window
                "ShellCmd": container["ShellCmd"],
                "InitCmd": container["InitCmd"],
                "DeleteCmd": container["DeleteCmd"],
                "ReadCmd": container["ReadCmd"]
            }
            #Check if the container exists in your system
            if alias in res.stdout.decode("utf-8").replace("'", ''):
                logger.info("Container '{0}' found".format(alias))
                _container["Status"] = 0
            else:
                logger.info(_("Container '{0}' not found".format(alias)))

            containers.append(_container)

        return containers

### OWASP CONTAINERS

    def __get_owasp_containers(self) -> list:
        if not self.supported:
            return []

        res = self.pulled_containers
        if res.returncode != 0:
            logger.error(_("Unable to get containers. Check if docker daemon is running."))
            return []
            
        containers = []
        for alias, container in self.__owasp_containers.items():
            _container = {
                "Name": container["Name"],
                "Status": 1,
                "Alias": alias,
                "ShellCmd": container["ShellCmd"],
                "InitCmd": container["InitCmd"],
                "DeleteCmd": container["DeleteCmd"],
                "ReadCmd": container["ReadCmd"]
            }
            #Check if the container exists in your system
            if alias in res.stdout.decode("utf-8").replace("'", ''):
                logger.info("Container '{0}' found".format(alias))
                _container["Status"] = 0
            else:
                logger.info(_("Container '{0}' not found".format(alias)))

            containers.append(_container)

        return containers

### ADDITIONAL CONTAINERS

    def __get_additional_containers(self) -> list:
        if not self.supported:
            return []

        res = self.pulled_containers
        if res.returncode != 0:
            logger.error(_("Unable to get containers. Check if docker daemon is running."))
            return []
            
        containers = []
        for alias, container in self.__additional_containers.items():
            _container = {
                "Name": container["Name"],
                "Status": 1,
                "Alias": alias,
                "ShellCmd": container["ShellCmd"],
                "InitCmd": container["InitCmd"],
                "DeleteCmd": container["DeleteCmd"],
                "ReadCmd": container["ReadCmd"]
            }
            #Check if the container exists in your system
            if alias in res.stdout.decode("utf-8").replace("'", ''):
                logger.info("Container '{0}' found".format(alias))
                _container["Status"] = 0
            else:
                logger.info(_("Container '{0}' not found".format(alias)))

            containers.append(_container)

        return containers

### PLATFORM CONTAINERS

    def __get_platforms(self) -> list:
        if not self.supported:
            return []

        res = self.pulled_containers
        if res.returncode != 0:
            logger.error(_("Unable to get containers. Check if docker daemon is running."))
            return []
            
        containers = []
        for alias, container in self.__managed_platforms.items():
            _container = {
                "Name": container["Name"],
                "Status": 1,
                "Alias": alias,
                "ShellCmd": container["ShellCmd"],
                "InitCmd": container["InitCmd"],
                "DeleteCmd": container["DeleteCmd"],
                "ReadCmd": container["ReadCmd"]
            }
            #Check if the container exists in your system
            if alias in res.stdout.decode("utf-8").replace("'", ''):
                logger.info("Container '{0}' found".format(alias))
                _container["Status"] = 0
            else:
                logger.info(_("Container '{0}' not found".format(alias)))

            containers.append(_container)

        return containers

### CUSTOM CONTAINERS

    def __get_custom_containers(self) -> list:
        if not self.supported:
            return []

        res = self.pulled_containers
        if res.returncode != 0:
            logger.error(_("Unable to get containers. Check if docker daemon is running."))
            return []
            
        containers = []
        for alias, container in self.__custom_containers.items():
            _container = {
                "Name": container["Name"],
                "Status": 1,
                "ID": container["ID"],
                "Alias": alias,
                "ShellCmd": container["ShellCmd"],
                "InitCmd": container["InitCmd"],
                "DeleteCmd": container["DeleteCmd"],
                "ReadCmd": container["ReadCmd"]
            }
            #Check if the container exists in your system
            if alias in res.stdout.decode("utf-8").replace("'", ''):
                logger.info("Container '{0}' found".format(alias))
                _container["Status"] = 0
            else:
                logger.info(_("Container '{0}' not found".format(alias)))

            containers.append(_container)

        return containers
