'use strict';

var gulp = require('gulp'),
    stylus = require('gulp-stylus'),
    myth = require('gulp-myth'),
    concat = require('gulp-concat'),
    rename = require('gulp-rename'),
    cssmin = require('gulp-csso'),
    plumber = require('gulp-plumber'),
    uglify = require('gulp-uglify'),
    riot = require('gulp-riot');

var paths = {
    styl: 'assets/styl/',
    js: 'assets/js/',
    tags: 'assets/tags/',
    tmp: 'assets/tmp/',
    static: {
        css: 'static/css/',
        js: 'static/js/'
    }

};

gulp.task('build', function() {
    gulp.start('styles', 'scripts', 'riot', 'watch')
});

gulp.task('watch', function() {
    gulp.watch(paths.styl + '*.styl', function() {
        gulp.start('styles');
    });

    gulp.watch(paths.js + '*.js', function() {
        gulp.start('scripts');
    })

    gulp.watch(paths.tags + '*.tag', function() {
        gulp.start('riot');
    })

    gulp.watch(paths.tmp + '*.js', function() {
        gulp.start('gluejs');
    })
});

gulp.task('riot', function() {
   return gulp.src(paths.tags + '*.tag')
        .pipe(plumber())
        .pipe(riot())
        .pipe(concat('tags.js'))
        .pipe(gulp.dest(paths.tmp))
});

gulp.task('styles', function() {
    return gulp.src(paths.styl + 'layout.styl')
        .pipe(plumber())
        .pipe(stylus())        
        .pipe(myth())
        .pipe(rename('main.css'))
        .pipe(cssmin())
        .pipe(gulp.dest(paths.static.css));
});

gulp.task('scripts', function() {
    return gulp.src(paths.js + '*.js')
        .pipe(plumber())
        .pipe(concat('libs.js'))
        .pipe(gulp.dest(paths.tmp))
});

gulp.task('gluejs', function() {
    return gulp.src(paths.tmp + '*.js')
        .pipe(plumber())
        .pipe(concat('scripts.js'))
        .pipe(uglify())
        .pipe(gulp.dest(paths.static.js))
});

