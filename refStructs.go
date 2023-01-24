package bbg

type pyOutput struct {
	Responses       []Response
	ResponseErrors  []ResponseError
	SecurityErrors  []SecurityError
	FieldExceptions []FieldException
}

type Response struct {
	Ticker         string
	Field          string
	Value          interface{}
	SequenceNumber int
}

type ResponseError Error

type Error struct {
	Source      string
	Code        int
	Category    string
	Message     string
	Subcategory string
}

type SecurityError struct {
	Ticker         string
	SequenceNumber int
	Error
}

type FieldException struct {
	Ticker         string
	SequenceNumber int
	Error
}
