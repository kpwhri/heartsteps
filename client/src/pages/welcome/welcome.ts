import { Component, OnInit, ElementRef, Renderer2 } from '@angular/core';
import { IonicPage, NavController, ModalController } from 'ionic-angular';
import { EnrollmentModal } from '@heartsteps/enrollment/enroll';

@Component({
  selector: 'page-welcome',
  templateUrl: 'welcome.html',
  entryComponents: [
    EnrollmentModal
  ]
})
export class WelcomePage implements OnInit {

  constructor(
    private el:ElementRef,
    private renderer:Renderer2,
    private modalCtrl: ModalController
  ) {}

  goToEnrollPage() {
    let modal = this.modalCtrl.create(EnrollmentModal);
    modal.present();
  }

  ngOnInit() {
    this.renderer.addClass(this.el.nativeElement, 'start-screen')
  }

}
