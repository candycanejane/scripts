package main

import (
    "fmt"
    "os"
    "bufio"
    "strings"
    "net/http"
    "log"
)

var concurrency = 10

// check is a simple function to handle errors
func check(e error) {
    if e != nil {
    	log.Fatal(e)
    }
}

// fetch performs a GET request for a given URL and checks the HTTP response header
// for specific options that indicate clickjack protection is enabled
func fetch(checker_ch, results_ch chan string) {
	for url := range checker_ch {
		resp, err := http.Get(url)
		check(err)
	
		// check header field for X-Frame-Options
		// Ref: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options
		elem, ok := resp.Header["X-Frame-Options"]
		if ok {
			results_ch <- fmt.Sprintf("%s: %v\n", url, elem)
			return 
		}
		results_ch <- fmt.Sprintf("%s: No results.\n", url)
	}
}

func main() {
	// create channels for passing around this work
	checker_ch := make(chan string)
	results_ch := make(chan string)
	done := make(chan bool)
	
	// reads lines from a CSV file into work queue
	go func() {
		inFile, err := os.Open("/Users/Jody/go/src/github.com/candycanejane/click_jack/test_urls.txt")
		check(err)
    	defer inFile.Close()
    	scanner := bufio.NewScanner(inFile)
    
    	// parse CSV and extract URL
    	for scanner.Scan() {
    		line := scanner.Text()
    		parts := strings.Split(line, ",")
    		url := "http://www." + parts[1]
    		checker_ch <- url
    	}
    	// close channel when we're done reading
    	close(checker_ch)
	}()

	// check multiple URLs at a time
	for i := 0; i < concurrency; i++ {
		go fetch(checker_ch, results_ch)
	}
	
	// pull from results queue and write results to file
	go func() {
		// open file for writing
		f, err := os.Create("/Users/Jody/go/src/github.com/candycanejane/click_jack/results.txt")
		defer f.Close()
		check(err)
	
		for result := range results_ch {
			f.WriteString(result)
    		f.Sync()
		}
		// signal we're done
		close(results_ch)
		done <- true
	}()
	
	// Wait for everyone to finish
	for i := 0; i < concurrency; i++ {
		<-done
	}
}

