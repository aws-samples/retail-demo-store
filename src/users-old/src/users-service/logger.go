// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"log"
	"net/http"
	"time"
)

// loggingResponseWriter Struct
type loggingResponseWriter struct {
	http.ResponseWriter
	statusCode int
}

// NewLoggingResponseWriter Function
func NewLoggingResponseWriter(w http.ResponseWriter) *loggingResponseWriter {
	return &loggingResponseWriter{w, http.StatusOK}
}

//WriteHeader Function
func (lrw *loggingResponseWriter) WriteHeader(code int) {
	lrw.statusCode = code
	lrw.ResponseWriter.WriteHeader(code)
}

// Logger Function
func Logger(inner http.Handler, name string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		lrw := NewLoggingResponseWriter(w)

		inner.ServeHTTP(lrw, r)

		statusCode := lrw.statusCode

		// Log Response
		log.Printf(
			"%s\t%s\t%s\t%d\t%s",
			r.Method,
			r.RequestURI,
			name,
			statusCode,
			time.Since(start),
		)

	})
}
