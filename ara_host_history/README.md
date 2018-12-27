# ara_host_history

Generates HTML overview showing playbook run history by host as stored by [ARA](https://ara.readthedocs.io).

## Why this script?

We would like to know which hosts were most recently targeted by Ansible runs, and what the result was. It comes as no surprise that there is no such info recorded by default, since Ansible is server and agent-less. To that end, [ARA](https://ara.readthedocs.io/en/stable/) exists, and comes very close to our wish. However, it gives a playbook-based overview only, not a host-based one.

Note: We're using this one it with Ansible 2.7.5, Python 2.7.

## How does it work?

As you might guess, this script requires a working [ARA](https://ara.readthedocs.io/en/stable/) install first. Ansible playbook runs are by default recorded into an SQLite DB by ARA.

We leverage that SQLite DB to retrieve information about playbook runs performed by Ansible.

The HTML overview is generated using a Jinja2 template. Links to ARA are included, in order to be able to drill-down into the individual items.

## Usage

Run `ara_host_history.py` which by default will look for the DB in the `.ara/` directory in the current user's home.

By default, output is generated in `/srv/www/htdocs/ara_host_history.html` **We do not create the folder. We do not know where your webserver runs. The folder has to exist already.** Modify using `--out`.

It is highly recommended to specify the webserver URL of your ARA instance using `--ara`, otherwise drill-down will not be possible. Additionally, if [ansible-cmdb](https://github.com/fboender/ansible-cmdb) is installed, links to its results can be created using `--cmdb`. Links are created relatively to the host ara_host_history output is loaded from, unless an absolute URL is given.

Example command line: `python2 ./ara_host_history.py --cmdb /cmdb --ara http://ansible:8080`
	
The overview page will compute the overall status of the latest individual hosts' playbook run as follows:
* OK if all tasks of all plays contained in the playbook returned status "ok"
* SKIPPED if any task of any play contained in the playbook returned status "skipped"
* UNREACHABLE if any task of any play contained in the playbook returned status "unreachable"
* FAILED if any task of any play contained in the playbook returned status "failed"
They do so in that order, e.g.: If there are skipped as well as unreachable statuses reported, "unreachable" will be shown. "Failed" is the worst status: if a single task has failed, the overall status of that playbook will be "failed", no matter what all other statuses are.

### Command line options
(see also `ara_host_history.py -h`)

* `--db`: Location of the ARA DB, default: `~/.ara/ansible.sqlite`
* `--out`: The output location, default: `/srv/www/htdocs/ara_host_history.html`
* `--loglevel`: The log level, one of CRITICAL, ERROR, WARNING, INFO, DEBUG, default: `INFO`
* `--cmdb`: URL to ansible-cmdb directory (optional), default: None
* `--ara`: URL to ARA webserver (optional), default: None

## What does the result look like?

![ARA Host History screenshot](ara_host_history_screenshot.png?raw=true "ARA Host History screenshot")

## Development notes

* There is one entry in the hosts table for EACH RUN of a PLAYBOOK ("id" is NOT a host id!) Each host appears many times.
* Also, each playbook path does appear with many ids.
* There are no repeating id values anywhere, as id is always the primary key.
* We are sorting directly via SQL ORDER BY and outputting lists. That is easier than sorting dictionaires later on.
* We have "borrowed" some CSS definitions from the excellent [ansible-cmdb](https://github.com/fboender/ansible-cmdb) project.
* Data structure: `[ [ { playbook: plays [ { play: tasks [ { task: task_result {} } ] } ] } ] ]`
