import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {

    tabs:Array<any> = [{
        name:'Dashboard',
        key: 'dashboard'
    }, {
        name: 'Planning',
        key: 'planning'
    }, {
        name: 'Stats',
        key: 'stats'
    }, {
        name: 'Learn',
        key: 'learn'
    }];

    constructor(
        private router: Router
    ) {

    }
}
