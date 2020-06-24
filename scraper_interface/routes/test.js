
var request = require('request');
var express = require('express');
var router = express.Router();

/* GET home page. */
router.post('/', function(req, res, next) {
  var name = req.body.name;
  var url = req.body.url;
  var hooks = [];
  
  var names = req.body.names;
  var selectors = req.body.selectors;
  var callbacks = req.body.callbacks;
  var len = req.body.names.length;

  console.log(names);
  console.log(selectors);
  console.log(callbacks);
  
  if (names instanceof Array) {
    for (let i = 0; i < len; i++) {
      var n = names[i];
      hooks.push({
        n : {
          "selector": selectors[i],
          "callback": callbacks[i]
        }
      });
    }
  } else {
    hooks = {
      names : {
        "selector": selectors,
        "callback": callbacks
      }
    }
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
      if (err) { return res.status(500).end("redirect err"); }
        //res.writeHead(json); // copy all headers from remoteResponse
        // console.log(remoteRes);
        // console.log(remoteBody);
        res.send(remoteBody);
    }
  );
});

module.exports = router;
