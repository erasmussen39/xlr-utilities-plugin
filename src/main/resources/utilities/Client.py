#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from com.xebialabs.xlrelease.domain.variables import StringVariable

class Client(object):
    def __init__(self):
        return

    @staticmethod
    def get_client():
        return Client()

    @staticmethod
    def getCurrentPhase(variables):
        current_phase = variables['getCurrentPhase']
        return current_phase()

    @staticmethod
    def find_variable_with_key(key, variables):
        for variable in variables:
            if variable.getKey() == key:
                return variable

    @staticmethod
    def find_template_with_name(name, variables):
        templates = variables['templateApi'].getTemplates(name)
        return templates[0]

    @staticmethod
    def add_task(variables, container, task_type, title):
        task = variables['taskApi'].newTask(task_type)
        task.title = title
        return variables['taskApi'].addTask(container, task).getId()

    @staticmethod
    def get_release_vars(variables, iteration):
        release_vars = []
        for variable in variables['release_variables'][iteration].split(','):
            key_value = variable.split("=")
            v = StringVariable()
            v.setKey(key_value[0])
            v.setValue(key_value[1])
            release_vars.append(v)
        return release_vars

    @staticmethod
    def generate_create_release_task(variables, release_title, template_name, iteration):
        task = variables['taskApi'].newTask("xlrelease.CreateReleaseTask")
        task.title = release_title
        task.newReleaseTitle = release_title
        task.templateId = "%s" % Client.find_template_with_name(template_name, variables).getId()
        task.createdReleaseId = "${RELEASE_ID%s}" % iteration
        if len(variables['release_variables']) > iteration:
            task.templateVariables = Client.get_release_vars(variables, iteration)
        return task

    @staticmethod
    def generate_gate_task(variables, release_title, gates_container, iteration):
        task = variables['taskApi'].newTask("xlrelease.GateTask")
        task.title = "Wait For Completion of %s" % release_title
        gate_id = variables['taskApi'].addTask(gates_container, task).getId()
        variables['taskApi'].addDependency(gate_id, "${RELEASE_ID%s}" % iteration)

    @staticmethod
    def generate_create_sub_releases(variables, releases_container, gates_container):
        tasks = []
        release_templates = variables['release_templates']
        release_titles = variables['release_titles']
        i = 0
        for template_name in release_templates:
            if (len(release_titles) <= i) or not release_titles[i]:
                release_title = template_name
            else:
                release_title = release_titles[i]
            task = Client.generate_create_release_task(variables, release_title, template_name, i)
            tasks.append(variables['taskApi'].addTask(releases_container, task).getId())
            if variables['create_gates']:
                Client.generate_gate_task(variables, release_title, gates_container, i)
            i += 1
        return tasks

    @staticmethod
    def generate_subrelease(variables):
        releases_container = Client.getCurrentPhase(variables).getId()
        gates_container = Client.getCurrentPhase(variables).getId()
        if variables['parallel']:
            releases_container = Client.add_task(variables, Client.getCurrentPhase(variables).getId(), "xlrelease.ParallelGroup", "Start Releases")
            gates_container = Client.add_task(variables, Client.getCurrentPhase(variables).getId(), "xlrelease.ParallelGroup", "Wait For Releases")
        return Client.generate_create_sub_releases(variables, releases_container, gates_container)

    @staticmethod
    def utilities_generatesubreleases(variables):
        task_ids = Client.generate_subrelease(variables)
        return {"output" : "%s" % task_ids}
