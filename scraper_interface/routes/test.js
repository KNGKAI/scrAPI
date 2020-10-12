
var request = require('request');
var express = require('express');
var router = express.Router();

router.post('/', function(req, res, next) {
  console.log("testing.....");
  console.log(req.body);

  var name = req.body.name;
  var url = req.body.url;
  var hooks = [];
  
  var names = req.body.names;
  var selectors = req.body.selectors;
  var callbacks = req.body.callbacks;
  
  if (names instanceof Array) {
    for (let i = 0; i < req.body.names.length; i++) {
      hooks.push({
        "name": names[i],
        "hook": {
          "selector": selectors[i],
          "callback": callbacks[i]
        }
      });
    }
  } else {
    hooks = [{
      "name": names,
      "hook": {
        "selector": selectors,
        "callback": callbacks
      }
    }];
  }

  var json = JSON.stringify({
    "name": name,
    "url": url,
    "hooks": hooks
  });

  console.log(json);

  var url = 'https://scrapi-scraper.azurewebsites.net/api/scraper-http-trigger';
  
  var options = {
    method: 'post',
    body: json,
    url: url
  }
  
  request(options,
    function(err, remoteRes, remoteBody) {
      if (err) {
        return remoteRes.status(500).end("remote_error");
      }
      res.send({ result: remoteBody });
    }
  );
});

module.exports = router;
