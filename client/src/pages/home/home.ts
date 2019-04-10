import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, RouterEvent, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';

class Tab {
    name:string;
    key: string;
}

@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage implements OnInit, OnDestroy {
    public pageTitle: string;
    public activeTab: string;
    public backButton: boolean;

    private routerSubscription: Subscription;
     
    public tabs:Array<Tab> = [{
        name:'Dashboard',
        key: 'dashboard'
    }, {
        name: 'Planning',
        key: 'planning'
    }, {
        name: 'Stats',
        key: 'stats'
    }, {
        name: 'Settings',
        key: 'settings'
    }];

    constructor(
        private router: Router
    ) {}

    ngOnInit() {
        this.updateFromUrl(this.router.url);
        this.routerSubscription = this.router.events
        .filter(event => event instanceof NavigationEnd)
        .subscribe((event:RouterEvent) => {
            this.updateFromUrl(event.url);
        });
    }

    ngOnDestroy() {
        this.routerSubscription.unsubscribe();
    }

    private updateFromUrl(url:string) {
        this.getActiveTab(url)
        .then((activeTab: Tab) => {
            this.pageTitle = activeTab.name;
            this.activeTab = activeTab.key;
        })
        .catch(() => {
            console.log('No matching tab found');
        });
    }

    private getActiveTab(url:string):Promise<Tab> {
        return new Promise((resolve, reject) => {
            const matchingTab = this.tabs.find((tab) => {
                return url.indexOf(tab.key) >= 0
            });

            if(matchingTab) {
                resolve(matchingTab);
            } else {
                reject('No matching tab');
            }
        });
    }
}
