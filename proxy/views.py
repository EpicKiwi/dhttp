def dtn_sent(eid, agent, path):
    return """<!DOCTYPE html>
<html>
    <head>
        <title>Request sent to {eid}/{agent}{path}</title>
        <meta charset="utf-8" />
        <style>
        :root {{ font-family: sans-serif; }}
        body {{ box-sizing: border-box; width: 100%; max-width: 1000px; margin-left: auto; margin-right: auto; padding: 50px 10px; }}
        hr {{ border: none; height: 50px; }}
        </style>
    </head>
    <body>
        <p>We sent your messsage over a Delay Tolerant Network. We may receive a response someday.</p>
        <p>Be patient and retry later...</p>

        <hr />

        <pre>
EID     : {eid}
Agent   : {agent}
Path    : {path}
        </pre>
    </body>  
</html>
""".format(eid=eid, agent=agent, path=path)

def bad_url(invalid_path):
    return """<!DOCTYPE html>
<html>
    <head>
        <title>dhttp Proxy : Bad URL format</title>
        <meta charset="utf-8" />
        <style>
        :root {{ font-family: sans-serif; }}
        body {{ box-sizing: border-box; width: 100%; max-width: 1000px; margin-left: auto; margin-right: auto; padding: 50px 10px; }}
        hr {{ border: none; height: 50px; }}
        </style>
    </head>
    <body>
        <p>URL provided isn't a valid dhttp proxy URL</p>
        <p>Valid URL are using the following format</p>
        <pre><code>/&lt;eid&gt;/&lt;agent&gt;[/&lt;path&gt;]</code></pre>
    </body>  
</html>
""".format(path=invalid_path)