#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import base64, csv, getpass, json, os.path, sys, urllib2

print "CSV File:",
csv_file = raw_input()
if not os.path.isfile(csv_file):
    print "Specified CSV file %s does not exist." % csv_file
    sys.exit(1)
print "New Template Name:",
template_name = raw_input()
print "Enter XL Release URL:",
xlr_url = raw_input()
print "Enter XL Release Username:",
xlr_user = raw_input()
xlr_pass = getpass.getpass("Enter XL Release Password: ")

# Defaults
if not xlr_url:
    xlr_url = "http://localhost:5516"
if not xlr_user:
    xlr_user = "admin"
if not xlr_pass:
    xlr_pass = "admin"

opener = urllib2.build_opener(urllib2.HTTPHandler)

data = '''{
  "id" : "Applications/Release1",
  "type" : "xlrelease.Release",
  "title" : "%s",
  "scheduledStartDate" : "2017-10-21T21:05:07.014+02:00",
  "status" : "TEMPLATE"
}''' % template_name

headers = {"Content-Type" : "application/json" , "Authorization" : "Basic %s" % base64.b64encode("%s:%s" % (xlr_user, xlr_pass))}

request = urllib2.Request('%s/api/v1/templates/' % xlr_url, data, headers)
response = opener.open(request)

template = json.load(response)

if response.getcode() != 200:
    raise Exception("Failed to create new template: %s" % template_name)

# Delete unnecessary "New Phase"
request = urllib2.Request('%s/api/v1/phases/%s' % (xlr_url, template['phases'][0]['id']), data, headers)
request.get_method = lambda: 'DELETE'
response = opener.open(request)

phases = []
with open(csv_file, 'rb') as csvfile:
    template_reader = csv.reader(csvfile, delimiter=',')
    for row in template_reader:
        if not row[0] in phases:
            phases.append(row[0])

phase_name_id_map = {}
for phase_name in phases:
    data = "{'id' : '', 'type' : 'xlrelease.Phase', 'title' : '%s', 'release' : '%s', 'status' : 'PLANNED'}" % (phase_name, template['id'])
    request = urllib2.Request('%s/api/v1/phases/%s/phase' % (xlr_url, template['id']), data, headers)
    response = opener.open(request)
    phase = json.load(response)
    phase_name_id_map[phase_name] = phase['id']
    if response.getcode() != 200:
        raise Exception("Failed to create new phase: %s in template: %s" % (phase_name, template_name))

# Create Tasks
with open(csv_file, 'rb') as csvfile:
    template_reader = csv.reader(csvfile, delimiter=',')
    for row in template_reader:
        phase_id = phase_name_id_map[row[0]]
        data = "{'id' : '', 'type' : 'xlrelease.Task', 'title' : '%s', 'description' : '%s'}" % (row[1], row[2])
        request = urllib2.Request('%s/api/v1/tasks/%s/tasks' % (xlr_url, phase_id), data, headers)
        response = opener.open(request)
        task = json.load(response)
        if response.getcode() != 200:
            raise Exception("Failed to create new task %s." % row[1])
        if row[3]:
            request = urllib2.Request('%s/api/v1/tasks/%s/assign/%s' % (xlr_url, task['id'], row[3]), data=None, headers=headers)
            request.get_method = lambda: 'POST'
            response = opener.open(request)
        if response.getcode() != 200:
            raise Exception("Failed to assign task %s to %s." % (row[1], row[3]))
