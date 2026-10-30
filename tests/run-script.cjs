const fs = require("node:fs");
const vm = require("node:vm");
const script = fs.readFileSync(process.argv[2], "utf8");
const input = fs.readFileSync(0, "utf8");
const context = vm.createContext({});
vm.runInContext(script, context, {timeout: 2000});
if (process.argv[3] === "snapshot") {
  process.stdout.write(vm.runInContext(
    "JSON.stringify({USER_RULES,REGION_FILTERS,NODE_EXCLUDE_FILTER,TEST_URL,groupBase,SERVICE_GROUP_OPTIONS,ruleProviders,rules,proxyGroups})",
    context, {timeout: 2000}));
} else {
  context.inputJSON = input;
  process.stdout.write(vm.runInContext("JSON.stringify(main(JSON.parse(inputJSON)))", context, {timeout: 2000}));
}

