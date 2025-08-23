require('dotenv').config({ path: '../.env' });
const fetch = require('node-fetch');

const URL_API_ID = process.env.APPSYNC_API_ID;
const REGION = process.env.AWS_REGION;
const API_KEY = process.env.APPSYNC_API_KEY;

const MUTATION = `
mutation CreateChat($title: String!, $userId: ID!) {
  createChat(title: $title, userId: $userId) {
    id
    userId
    title
    createdAt
  }
}
`;

const VARIABLES = {
  title: process.env.CHAT_TITLE || 'Novo Chat',
  userId: process.env.USER_ID || ''
};

const url = `https://${URL_API_ID}.appsync-api.${REGION}.amazonaws.com/graphql`;

(async () => {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
      },
      body: JSON.stringify({
        query: MUTATION,
        variables: VARIABLES,
      }),
    });

    const data = await res.json();
    console.log('✅ Chat criado:', data);
  } catch (err) {
    console.error('❌ Erro ao criar chat:', err);
  }
})();
