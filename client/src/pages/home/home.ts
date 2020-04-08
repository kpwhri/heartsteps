import { Component, OnInit, OnDestroy, ElementRef, ViewChild } from '@angular/core';
import { Router, RouterEvent, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';
import { ParticipantService } from '@heartsteps/participants/participant.service';

class Tab {
    name:string;
    key: string;
}

@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage implements OnInit, OnDestroy {
    @ViewChild('#home-container') container: ElementRef;

    public pageTitle: string;
    public activeTab: string;
    public backButton: boolean;

    public updatingParticipant: boolean;
    public updatingParticipantSubscription: Subscription;

    private routerSubscription: Subscription;
    
    public tabs:Array<Tab> = [{
        name:'Dashboard',
        key: 'dashboard'
    }, {
        name: 'Planning',
        key: 'planning'
    }, {
        name: 'Activities',
        key: 'activities'
    }, {
        name: 'Settings',
        key: 'settings'
    }];

    constructor(
        private router: Router,
        private element: ElementRef,
        private participantService: ParticipantService
    ) {}

    ngOnInit() {
        this.updateFromUrl(this.router.url);
        this.routerSubscription = this.router.events
        .filter(event => event instanceof NavigationEnd)
        .subscribe((event:RouterEvent) => {
            this.updateFromUrl(event.url);
        });
        this.updatingParticipantSubscription = this.participantService.updatingParticipant.subscribe((isUpdating) => {
            this.updatingParticipant = isUpdating;
        });
    }

    ngOnDestroy() {
        this.routerSubscription.unsubscribe();
        this.updatingParticipantSubscription.unsubscribe();
    }

    private updateFromUrl(url:string) {
        this.getActiveTab(url)
        .then((activeTab: Tab) => {
            if(this.activeTab !== activeTab.key) {
                this.element.nativeElement.querySelector('#home-content').scrollTop = 0;
            }
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
