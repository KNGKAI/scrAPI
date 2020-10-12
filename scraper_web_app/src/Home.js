import React from 'react';

import ListGroup from 'react-bootstrap/ListGroup'

import Scrape from './Scrape';

const request = require('request');

class Home extends React.Component {
    constructor() {
        super();
        this.state = {
            result: "none",
            list: [
                {
                    name: "Random Wiki Page",
                    url: "https://en.wikipedia.org/wiki/Special:Random",
                    hooks: [
                        {
                            name: "title",
                            hook: {
                                selector: "h1",
                                callback: "get_text"
                            }
                        },
                        {
                            name: "body",
                            hook: {
                                selector: "div#bodyContent",
                                callback: "get_text"
                            }
                        }
                    ]
                },
            ],
        };
    }

    async scrape(data) {
        var body = JSON.stringify(data);
        this.setState({ result: body + ", scraping..."})

        request({
                url: 'https://scrapi-scraper.azurewebsites.net/api/scraper-http-trigger',
                method: 'post',
                body: body
            },
            (error, response, body) => {
                this.setState({
                    result: error || response.statusCode !== 200 ? error.message : JSON.stringify(body)
                });
            }
        )

        // fetch('https://scrapi-scraper.azurewebsites.net/api/scraper-http-trigger', {
        //     headers : {
        //         'Access-Control-Allow-Origin': '*',
        //         'Content-Type': 'application/json',
        //         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
        //     },
        //     method: 'POST',
        //     body: body
        // })
        // .then(res => JSON.stringify(res.json()))
        // .then(
        //   (result) => {
        //     this.setState({
        //         result: result
        //     });
        //   },
        //   // Note: it's important to handle errors here
        //   // instead of a catch() block so that we don't swallow
        //   // exceptions from actual bugs in components.
        //   (error) => {
        //     this.setState({
        //         result: "error"
        //     });
        //   }
        // )
        // // result = JSON.stringify(result.json());
        // console.log(result);
        // this.setState({ result: result });
    }

    render() {
        return <div>
            <h1>ScaAPI</h1>
            <ListGroup variant="flush">
                {this.state.list.map((item, index) => {
                    return <Scrape
                        key={index}
                        index={index}
                        name={item.name}
                        url={item.url}
                        hooks={item.hooks}
                    />
                })}
            </ListGroup>
            <button onClick={() => this.scrape(this.state.list)}>Scrape</button>
            <div>
                <h2>Result:</h2>
                <p>{this.state.result}</p>
            </div>
        </div>;
    }
}

export default Home;
