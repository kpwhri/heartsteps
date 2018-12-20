import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, RouterEvent } from '@angular/router';
import { Subscription } from 'rxjs';

@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage implements OnInit, OnDestroy {
    public pageTitle: string;
    public backButton: boolean;

    private routerSubscription: Subscription;
     
    public tabs:Array<any> = [{
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
        key: 'library'
    }, {
        name: 'Settings',
        key: 'settings'
    }];

    constructor(
        private router: Router
    ) {}

    ngOnInit() {
        this.updateWithUrl(this.router.url);
        this.routerSubscription = this.router.events.subscribe((event:RouterEvent) => {
            if(event.url) {
                this.updateWithUrl(event.url);
            }
        });
    }

    ngOnDestroy() {
        this.routerSubscription.unsubscribe();
    }

    private updateWithUrl(url:string) {
        this.setTitle(url);
    }

    private setTitle(url:string) {
        this.tabs.forEach((tab:any) => {
            if(url.indexOf(tab.key) > 0) {
                this.pageTitle = tab.name;
            }
        })
    }


}
