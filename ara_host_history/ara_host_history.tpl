<!DOCTYPE html>
<html>

<head>
<style type="text/css">
  *, body { font-family: sans-serif; font-size: 1em; }
  a { text-decoration: none; }
  b { font-weight: bold; }
  p { margin-bottom: 1em; }

  #host_overview { margin: 32px; }
  #host_overview h2 { display: block; color: #606060; }
  #host_overview_tbl_wrapper{ margin-left: 16px; }
  #host_overview table { width: 100%; clear: both; }
  #host_overview tr { border-bottom: 1px solid #F0F0F0; }
  #host_overview tr:hover { background-color: #F0F0F0; }
  #host_overview thead th { text-align: left; color: #707070; border-bottom: 1px solid #C0C0C0; font-weight: bold; }
  #host_overview tbody td { color: #000000; }
  #host_overview tbody a { text-decoration: none; color: #005c9d; }
  #host_overview tbody td.error a { color: #FF0000; }
  #host_overview .error { color: #FF0000; }
  #host_overview .small { font-size: 0.5em; }
  .generated { color: #a0a0a0; font-size: 0.8em; position: absolute; top: 0; right: 32px; }
</style>
</head>

<body>

<div class="generated">
<h3>ara_host_history &mdash; Generated {{ now() }}</h3>
</div>

<div id="host_overview">
<h2>Host overview: Latest playbook run of each host as seen by ARA</h2>

<table>

<thead>
<tr>
<th>Host</th>
<th>Last run ended</th>
<th>Last run started</th>
<th>Last playbook (# of plays)</th>
{# <th>Total playbooks</th> #}
<th>Overall Status</th>
</tr>
</thead>

<!--
Data structure: [ {host: [ { playbook: plays [ { play: tasks [ { task: task_result {} } ] } ] } ] } ]
-->

<tbody>
{% for hostpbs in history %}
{% set ovstat = hostpbs[0]['_overall_status'] %}
<tr>
<td class="{{ 'error' if ovstat != 'ok' }}">
{{ hostpbs[0]['name'] }}
{% if fl['cmdb'] %}
<span class="small">[<a href="{{fl['cmdb']}}/{{hostpbs[0]['name']}}.html">CMDB</a>]</span>
{% endif %}
{% if fl['ara'] %}
<span class="small">[<a href="{{fl['ara']}}/host/{{hostpbs[0]['host_id']}}/">ARA</a>]</span>
{% endif %}
</td>
<td>{{ hostpbs[0]['time_end'] }}</td> 
<td>{{ hostpbs[0]['time_start'] }}</td>
<td>
{{ hostpbs[0]['path'] }} ({{ hostpbs[0]['plays']|length }})
{% if fl['ara'] %}
<span class="small">[<a href="{{fl['ara']}}/reports/{{hostpbs[0]['playbook_id']}}.html">ARA</a>]</span>
{% endif %}
</td>
{# <td>{{ hostpbs|length }}</td> #}
<td>{{ ovstat }}</td>
</tr>
{% endfor %}
</tbody>

</table>

</div>

</body>

</html>
