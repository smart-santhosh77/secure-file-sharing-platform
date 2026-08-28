const SecureFileSharing = artifacts.require("SecureFileSharing");
const AccessControl = artifacts.require("AccessControl");

module.exports = function (deployer) {
  deployer.deploy(SecureFileSharing);
  deployer.deploy(AccessControl);
};
