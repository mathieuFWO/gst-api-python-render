const fs=require('fs'),path=require('path');const T='/tmp/claude-0/-home-claude/f6658268-8fe7-580d-9107-6939e43c6edb/scratchpad/repo/tests';
let src=fs.readFileSync(T+'/banc-v56-12-tableau.js','utf8').split('\n(async()=>{')[0].replace(/__dirname/g,JSON.stringify(T)).replace("require('playwright')","require(require.resolve('playwright',{paths:["+JSON.stringify(T)+",process.cwd()].concat(module.paths)}))");
fs.writeFileSync(__dirname+'/pw.js',src+'\n'+fs.readFileSync(__dirname+'/body.js','utf8'));
