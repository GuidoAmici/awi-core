// Read posts.js and generate SQL INSERT statements
const path = require('path');

// Import the posts data
const postsPath = path.resolve('D:/GitHub/GuidoAmici/newhaze-learn/src/constants/posts.js');

// We need to handle ES module syntax - read file and eval
const fs = require('fs');
let code = fs.readFileSync(postsPath, 'utf8');

// Convert ES module export to CommonJS and capture in global scope
code = code.replace('export const POST_CONTENT =', 'global.POST_CONTENT =');
eval(code);

// Generate SQL
function escapeSql(str) {
  if (str === null || str === undefined) return 'NULL';
  return "'" + String(str).replace(/'/g, "''") + "'";
}

let sql = '-- Migration: populate topic_content from posts.js\n';
sql += '-- Generated: ' + new Date().toISOString() + '\n\n';
sql += 'TRUNCATE topic_content;\n\n';

const ids = Object.keys(POST_CONTENT).map(Number).sort((a, b) => a - b);

for (const id of ids) {
  const p = POST_CONTENT[id];
  const chainJson = JSON.stringify(p.chain.items).replace(/'/g, "''");

  sql += `INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (\n`;
  sql += `  ${id},\n`;
  sql += `  ${escapeSql(p.title)},\n`;
  sql += `  ${escapeSql(p.variable)},\n`;
  sql += `  ${escapeSql(p.skill)},\n`;
  sql += `  ${escapeSql(p.objective)},\n`;
  sql += `  ${escapeSql(p.error.label)},\n`;
  sql += `  ${escapeSql(p.error.text)},\n`;
  sql += `  ${escapeSql(p.mechanism.label)},\n`;
  sql += `  ${escapeSql(p.mechanism.text)},\n`;
  sql += `  ${escapeSql(p.chain.label)},\n`;
  sql += `  '${chainJson}'::jsonb,\n`;
  sql += `  ${escapeSql(p.discard.label)},\n`;
  sql += `  ${escapeSql(p.discard.text)},\n`;
  sql += `  ${escapeSql(p.closing)}\n`;
  sql += `);\n\n`;
}

// Write SQL file
const outPath = 'D:/GitHub/GuidoAmici/second-brain/.claude/tmp/topic_content_data.sql';
fs.writeFileSync(outPath, sql, 'utf8');
console.log(`Generated ${ids.length} INSERT statements → ${outPath}`);
