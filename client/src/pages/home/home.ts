import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, RouterEvent, NavigationEnd, ActivatedRoute, RouterState } from '@angular/router';
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
            this.show('dashboard');
        });
    }

    private getActiveTab(url:string):Promise<Tab> {
        return new Promise((resolve, reject) => {
            let matchingTab:Tab = null;
            this.tabs.forEach((tab: Tab) => {
                const outputPath:string = '(home:' + tab.key + ')'
                if(url.indexOf(outputPath) >= 0) {
                    matchingTab = tab;
                }
            });

            if(matchingTab) {
                resolve(matchingTab);
            } else {
                reject('No matching tab');
            }
        });
    }

    public show(key:any) {
        this.router.navigate([{outlets: {home: key}}]);
    }


}
