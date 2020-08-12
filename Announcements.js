const req = require('@aero/centra');
require('dotenv').config();
const { MongoClient } = require('mongodb');

const main = async () => {
    const client = await MongoClient.connect(process.env.MONGO_URI, { useUnifiedTopology: true });
    const coll = client.db('youtube').collection('community');

    const site = await req('https://www.youtube.com/user/WatchMojo/community').text();

    let line = site.split('\n').find(s => s.includes('window["ytInitialData"]'));

    line = line.replace('window["ytInitialData"] = ', '');
    line = line.slice(0,line.length - 1);
    
    json = JSON.parse(line);

    const posts = json
        .contents
        .twoColumnBrowseResultsRenderer
        .tabs
        .find(obj => obj.tabRenderer.title === 'Community')
        .tabRenderer
        .content
        .sectionListRenderer
        .contents[0]
        .itemSectionRenderer
        .contents
        .map(item => {
            const post = item.backstagePostThreadRenderer.post.backstagePostRenderer;
            return {
                _id: post.postId,
                url: 'https://www.youtube.com/post/' + post.postId,
                content: post.contentText.runs.map(item => {
                    const { text } = item;
                    const url = item?.navigationEndpoint?.urlEndpoint?.url;
                    return url 
                        ? `[${text}](${url.startsWith('http') ? '' : 'https://youtube.com'}${url})`
                        : text;
                }).join('')
            }
        });
    
    for (const post of posts) {
        const exists = await coll.findOne({ _id: post._id });
        if (!exists) coll.insertOne({ ...post, posted: false });
    }


    client.close();
}

main();