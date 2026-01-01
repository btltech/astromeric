
// const fetch = require('node-fetch'); // Built-in in Node 18+

async function test() {
  const baseUrl = 'https://astronumeric-backend-production.up.railway.app';
  const endpoint = '/learn/modules';
  
  try {
    const resp = await fetch(`${baseUrl}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`API error ${resp.status}: ${text}`);
    }
    
    const data = await resp.json();
    console.log('Success:', JSON.stringify(data, null, 2));
  } catch (err) {
    console.error('Failed:', err);
  }
}

test();
