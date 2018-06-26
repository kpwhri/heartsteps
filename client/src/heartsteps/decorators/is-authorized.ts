
export function isAuthorized(target) {
    target.prototype.ionViewCanEnter = function() {
        console.log("howdy");
    }
}