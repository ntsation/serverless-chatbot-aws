const fetch = require('node-fetch');
const URL_API_ID = '';
const REGION = '';
const API_KEY = '';

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
  title: '',
  userId: ''
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
