package bbg

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os/exec"

	_ "embed"

	"github.com/cmarkh/errs"
)

//go:embed ref.py
var pyRef string

type Request struct {
	Tickers   []string
	Fields    []string
	Overrides []Override
	//SequenceNumber int
}

type Override struct {
	Field string
	Value string
}

func Ref(tickers []string, fields []string, overrides ...Override) (resp []Response,
	securityErrors []SecurityError, fieldErrors []FieldException, fatal error) {
	//respErrors []ResponseError,

	//sequenceNumber := rand.Intn(100)

	request, fatal := json.Marshal(Request{tickers, fields, overrides})
	if fatal != nil {
		fatal = errs.WrapErr(fatal)
		return
	}

	cmd := exec.Command("python", "-c", pyRef)
	cmd.Stdin = bytes.NewBuffer(request)

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	fatal = cmd.Run()
	if fatal != nil {
		fatal = errs.WrapErr(fatal, stderr.String())
		return
	}

	outBytes := stdout.Bytes()
	//fmt.Printf("out:\n%s\n", string(outBytes))

	pyResp := pyOutput{}
	fatal = json.Unmarshal(outBytes, &pyResp)
	if fatal != nil {
		fatal = errs.WrapErr(fatal) //, string(outBytes))
		fmt.Println(string(outBytes))
		return
	}

	if len(pyResp.ResponseErrors) != 0 {
		fatal = fmt.Errorf("response errors found: %v\n", fmt.Sprint(pyResp.ResponseErrors))
		return
	}

	return pyResp.Responses, pyResp.SecurityErrors, pyResp.FieldExceptions, fatal
}
