import { Component, ElementRef, Renderer2, OnInit } from "@angular/core";
import { Router, ActivatedRoute } from "@angular/router";
import { Message } from "@heartsteps/notifications/message.model";

@Component({
    selector: 'heartsteps-notification-page',
    templateUrl: './notification.page.html'
})
export class NotificationPage implements OnInit {
    private notification: Message;

    public title: string;
    public body: string;

    constructor(
        private el:ElementRef,
        private renderer:Renderer2,
        private router: Router,
        private route: ActivatedRoute
    ) {}

    ngOnInit() {
        this.notification = this.route.snapshot.data['notification'];
        this.title = this.notification.title;
        this.body = this.notification.body;

        this.renderer.addClass(this.el.nativeElement, 'start-screen');
    }

    public dismiss() {
        this.notification.engaged();
        this.router.navigate(['']);
    }

}
