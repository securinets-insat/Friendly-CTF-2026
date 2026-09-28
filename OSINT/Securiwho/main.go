package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"strings"
	"time"
)

const (
	FLAG             = "Securinets{Y0u_4r3_0n3_0f_u5_n0w}"
	MAX_MISTAKES     = 1
	QUESTION_TIMEOUT = 20 * time.Second
)

type Question struct {
	Question string
	Answers  []string
}

var questions = []Question{
	{
		"1 - In what year was Securinets founded?",
		[]string{
			"2003",
		},
	},
	{
		"2 - Who is the female co-founder of Securinets?",
		[]string{
			"Nihel Ben Youssef",
			"Nihel",
		},
	},
	{
		"3 - What is the official website of Securinets?",
		[]string{
			"securinets.tn",
			"www.securinets.tn",
			"https://securinets.tn",
			"https://www.securinets.tn",
		},
	},
	{
		"4 - What is the name of Securinets annual congress?",
		[]string{
			"Cybersphere",
			"CyberSphere",
		},
	},
	{
		"5 - What team won Securinets CTF 2025?",
		[]string{
			"aresx",
			"ARESx",
		},
	},
	{
		"6 - Whats the ctf weight of Securinets CTF Quals 2024?",
		[]string{
			"95.59",
		},
	},
	{
		"7 - Whats the name of the team that won Cybersphere 2025 beginner CTF?",
		[]string{
			"flag{sleep_404}",
			"sleep_404",
		},
	},
	{
		"8 - Who got 2nd place in the first edition of Darkest Hour ctf?",
		[]string{
			"cremetartinefabuleuse",
			"crémetartinéfabuleuse",
		},
	},
	{
		"9 - What is the name of the first competition that FL1TZ qualified to last year?",
		[]string{
			"CSAW",
		},
	},
	{
		"10 - INSAT Press and Securinets INSAT join forces for a 24-hour hackathon. Whats the event called?",
		[]string{
			"Unbreaking News",
		},
	},
}

// normalizeAnswer makes answer comparison more tolerant.
// It ignores:
// - Upper/lower case
// - Extra spaces
// - Common punctuation
// - Hyphens, underscores, etc.
func normalizeAnswer(s string) string {
	s = strings.ToLower(strings.TrimSpace(s))

	replacer := strings.NewReplacer(
		".", "",
		",", "",
		"!", "",
		"?", "",
		"'", "",
		"\"", "",
		"-", " ",
		"_", " ",
		"/", " ",
	)

	s = replacer.Replace(s)

	// Remove multiple consecutive spaces.
	s = strings.Join(strings.Fields(s), " ")

	return s
}

func send(conn net.Conn, message string) error {
	_, err := fmt.Fprintln(conn, message)
	return err
}

func disconnect(conn net.Conn) {
	send(conn, "")
	send(conn, "╔══════════════════════════════════════════════════╗")
	send(conn, "║                  ACCESS DENIED                  ║")
	send(conn, "╚══════════════════════════════════════════════════╝")
	send(conn, "")
	send(conn, "You have used your final attempt.")
	send(conn, "This connection has been terminated.")
	send(conn, "")
	send(conn, "[!] DISCONNECTING...")

	conn.Close()
}

func timeoutDisconnect(conn net.Conn) {
	send(conn, "")
	send(conn, "╔══════════════════════════════════════════════════╗")
	send(conn, "║                    TIMEOUT                     ║")
	send(conn, "╚══════════════════════════════════════════════════╝")
	send(conn, "")
	send(conn, "[!] You took too long to answer.")
	send(conn, "[!] Maximum time: 20 seconds.")
	send(conn, "[!] This connection has been terminated.")

	conn.Close()
}

func ask(
	conn net.Conn,
	reader *bufio.Reader,
	questionNumber int,
	question string,
	answers []string,
) (bool, bool) {

	send(conn, "")
	send(conn, fmt.Sprintf("┌──[ Question %d/10 ]", questionNumber))
	send(conn, fmt.Sprintf("│ %s", question))
	send(conn, "└──> ")

	// Start the 20-second timer.
	conn.SetReadDeadline(time.Now().Add(QUESTION_TIMEOUT))

	userAnswer, err := reader.ReadString('\n')

	// Remove the deadline after the answer.
	conn.SetReadDeadline(time.Time{})

	if err != nil {
		if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
			return false, true
		}

		return false, true
	}

	userAnswer = normalizeAnswer(userAnswer)

	// Compare against all accepted answers.
	for _, answer := range answers {
		if userAnswer == normalizeAnswer(answer) {
			return true, false
		}
	}

	return false, false
}

func handleConnection(conn net.Conn) {
	defer conn.Close()

	reader := bufio.NewReader(conn)
	mistakes := 0

	send(conn, "=======================================================")

	send(conn, `
                      %%#                                                    ##
                   %####                                                     #####%
                 %%####                                                       #######%
               %%%%###%                    ###############%                    #######%
             %%%%%%###            ##################################           #########
            %%%%%%%###       ############################################      #########%%
          %%%%%%%%###   ####################################################  #########%%%
          %%%%%%%%%###%  ####################################################  #########%%%
          %%%%%%%%%####  ###################################################  ###########%%%
         %%%%%%%%%%###### ################################################## ############%%%%
         %%%%%%%%%%######################################################################%%%%
        @%%%%%%%%%%######################################################################%%%%
        %%%%%%%%%%%######################################################################%%%%%
        %%%%%%%%%%%######################################################################%%%%%
        %%%%%%%%%%%######################################################################%%%%%
        %%%%%%%%%%%######################################################################%%%%%
        %%%%%%%%%%%######################################################################%%%%%
        %%%%%%%%%%%######################################################################%%%%%
        @%%%%%%%%%%######################################################################%%%%
         %%%%%%%%%%############ ###################################### ##################%%%%
         %%%%%%%%%%%####%######  #################################### ###################%%%
          %%%%%%%%% %#### ######  ################################## ######  ##### ######%%%
          %%%%%%%%%  ##### ######  ################################ ######  #####  ######%%
           %%%%%%%%   %####  #####  #############################  ######  ####    ######%
            %%%%%%%%    ####   #####  ##########################  ####    ####    ######%%
             %%%%%%#      ###    %###   ######################  %###     ###      ######%
              %%%%%%#       ##           ###################           ###       #######
                 %%###                       ############                      ######
                   ####                        ########                       #####
                    %###                         ####                        ###
                      %##                                                   %##%
                        %#                                                 ##
`)

	send(conn, "=======================================================")
	send(conn, "              WELCOME TO THE CHALLENGE")
	send(conn, "=======================================================")
	send(conn, "")
	send(conn, "You have 10 questions to answer.")
	send(conn, "You are allowed exactly ONE mistake.")
	send(conn, "A second mistake will terminate your connection.")
	send(conn, "You have 20 seconds for each question.")
	send(conn, "")
	send(conn, "Good luck.")
	send(conn, "=======================================================")

	for questionNumber, q := range questions {

		for {
			correct, timedOut := ask(
				conn,
				reader,
				questionNumber,
				q.Question,
				q.Answers,
			)

			if timedOut {
				timeoutDisconnect(conn)
				return
			}

			if correct {
				send(conn, "")
				send(conn, "[+] Correct!")
				break
			}

			mistakes++

			if mistakes > MAX_MISTAKES {
				disconnect(conn)
				return
			}

			send(conn, "")
			send(conn, "[!] Wrong answer.")
			send(conn, "[!] You have used your one mistake.")
			send(conn, "[!] Try the same question again.")
		}
	}

	send(conn, "")
	send(conn, "=======================================================")
	send(conn, "                 CHALLENGE COMPLETE")
	send(conn, "=======================================================")
	send(conn, "")
	send(conn, "[+] All 10 questions answered correctly!")
	send(conn, "[+] Access granted.")
	send(conn, "")
	send(conn, "FLAG: "+FLAG)
	send(conn, "")
	send(conn, "=======================================================")
}

func main() {
	listener, err := net.Listen("tcp", ":1337")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to start server: %v\n", err)
		os.Exit(1)
	}

	defer listener.Close()

	fmt.Println("[+] Challenge listening on :1337")

	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Fprintf(os.Stderr, "[!] Connection error: %v\n", err)
			continue
		}

		// One goroutine per player.
		go handleConnection(conn)
	}
}