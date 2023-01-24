package bbg

type ReferenceDataResponse struct {
	ResponseError Error
	SecurityData  []SecurityData
}

type SecurityData struct {
	Security        string
	SequenceNumber  int
	FieldData       []FieldData
	FieldExceptions []FieldException
	SecurityError   Error
}

type FieldData struct {
	Value interface{}
}

type FieldException struct {
	FieldID   string
	Message   string
	ErrorInfo Error
}

type Error struct {
	Source      string
	Code        int
	Category    string
	Message     string
	SubCategory string
}
