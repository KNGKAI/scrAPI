import React from 'react';

import ListGroup from 'react-bootstrap/ListGroup'

// callbackOptions = [
//     "get_text",
//     "get_href",
//     "get_content",
// ]

class Scrape extends React.Component {
    render() {
        return <ListGroup.Item key={this.props.index}>
            <div>
                Name: <input
                type="text"
                name="name"
                onChange={() => {}}
                value={this.props.name} />
                URL: <input
                type="text"
                name="url"
                onChange={() => {}}
                value={this.props.url} />
            </div>
            <div>
                {this.props.hooks.map((hook, index) => {
                    return <div key={index}>
                        Name: <input
                        type="text"
                        name="name"
                        onChange={() => {}}
                        value={hook.name} />
                        Selector: <input
                        type="text"
                        name="selector"
                        onChange={() => {}}
                        value={hook.hook.selector} />
                        Callback: <select
                        onChange={() => {}}
                        value={hook.hook.callback === "get_text" ? 0 : hook.hook.callback === "get_href" ? 1 : 2} >
                            <option value="get_text">Get Text</option>
                            <option value="get_href">Get HREF</option>
                            <option value="get_content">Get Content</option>
                        </select>
                    </div>
                })}
                <button>Add Hook</button>
            </div>
        </ListGroup.Item>;
    }
}

export default Scrape;
