import { Component, ViewChild, ElementRef } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';

declare var google;

@Component({
    selector: 'location-edit',
    templateUrl: 'location-edit.html'
})
export class LocationEdit {

    private address:String
    private type:String

    private lat:Number
    private lng:Number

    @ViewChild('map') mapElement: ElementRef
    private map:any

    private geocoder:any
    private geocoderTimeout:any

    private autocompletionService:any
    private addressPredictions:any

    private currentLocation:any

    constructor(
        params:NavParams,
        private viewCtrl:ViewController
    ) {
        const location = params.get('location')
        this.address = location.address
        this.type = location.type
        this.lat = location.lat
        this.lng = location.lng

        this.autocompletionService = new google.maps.places.AutocompleteService()
        this.geocoder = new google.maps.Geocoder()
    }

    ionViewDidLoad() {
        this.loadMap()
        this.placeMapPin()
    }

    update() {
        this.viewCtrl.dismiss({
            address: this.address,
            type: this.type,
            lat: this.lat,
            lng: this.lng
        })
    }

    showPredictions() {
        if(this.geocoderTimeout) {
            clearTimeout(this.geocoderTimeout)
        }

        this.geocoderTimeout = setTimeout(() => {
            this.geocoderTimeout = false
            this.getAddressPredicitions()
        }, 500)
    }

    getAddressPredicitions() {
        if(!this.address || this.address.length < 4) {
            this.addressPredictions = []
            return;
        }

        this.autocompletionService.getPlacePredictions({
            input: this.address
        }, (places, status) => {
            if(status != google.maps.places.PlacesServiceStatus.OK) {
                this.addressPredictions = []
            } else {
                if(places.length === 1) {
                    this.getLatLng(places[0].description)
                } else {
                    this.addressPredictions = places
                }
            }
        })
    }

    setAddress(address) {
        this.address = address
        this.addressPredictions = []
        this.getLatLng(address)
    }

    getLatLng(address) {
        this.geocoder.geocode({
            address: address
        }, (results, status) => {
            if(status === 'OK') {
                let result = results[0];
                this.updateLatLng(
                    result.geometry.location.lat(),
                    result.geometry.location.lng()
                )
            }
            
        })
    }

    updateLatLng(lat, lng) {
        this.lat = lat
        this.lng = lng
        this.placeMapPin()
    }

    loadMap() {
        if(this.lat && this.lng) {
            let latLng = new google.maps.LatLng(this.lat, this.lng);

            let mapOptions = {
                center: latLng,
                zoom: 10,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            }
           
            this.map = new google.maps.Map(this.mapElement.nativeElement, mapOptions);
        }
    }

    placeMapPin() {
        if(!this.lat || !this.lng) {
            return
        }
        if(!this.map) {
            this.loadMap()
        }
        
        let latLng = new google.maps.LatLng(this.lat, this.lng)
        this.map.setCenter(latLng)
        new google.maps.Marker({
            position: latLng,
            map: this.map
        });
    }
}
