const fetch = require('node-fetch');
const URL_API_ID = '';
const REGION = '';
const API_KEY = '';

const MUTATION = `
mutation CreateUser($email: String!) {
  createUser(email: $email) {
    id
    name
    email
    createdAt
  }
}
`;

const VARIABLES = {
  email: '',
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
    console.log('✅ Usuário criado:', data);
  } catch (err) {
    console.error('❌ Erro ao criar usuário:', err);
  }
})();
