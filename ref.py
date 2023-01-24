import blpapi
import sys
import dataclasses
from dataclasses import dataclass
import json
import datetime
# import time

responses = []          # [ticker, field, value]
response_errors = []    # [error]
security_errors = []    # [ticker, error]
field_exceptions = []       # [ticker, field, error]

@dataclass
class response:
    ticker: str = ""
    field: str = ""
    value: any = ""
    sequenceNumber: int = 0

@dataclass
class response_error:
    source: str = ""
    code: int = 0
    category: str = ""
    message: str = ""
    subcategory: str = ""

@dataclass
class security_error:
    ticker: str = ""
    sequenceNumber: int = 0
    source: str = ""
    code: int = 0
    category: str = ""
    message: str = ""
    subcategory: str = ""

@dataclass
class field_exception:
    ticker: str = ""
    sequenceNumber: int = 0
    field: str = ""
    source: str = ""
    code: int = 0
    category: str = ""
    message: str = ""
    subcategory: str = ""

def main():
    # start = time.time()

    try: 
        request = sys.stdin.readline()
        js = json.loads(request)

        session = blpapi.Session()

        if not session.start():
            sys.exit("Failed to start session.")

        if not session.openService("//blp/refdata"):
            sys.exit("Failed to open //blp/refdata")

        refDataService = session.getService("//blp/refdata")
        request = refDataService.createRequest("ReferenceDataRequest")

        for ticker in js['Tickers']:
            request.append("securities", ticker)

        for field in js['Fields']:
            request.append("fields", field)
        
        if 'Overrides' in js and js['Overrides'] is not None:
            for override in js['Overrides']:
                overrides = request.getElement('overrides')
                ovrd = overrides.appendElement()
                ovrd.setElement('fieldId', override['Field'])
                ovrd.setElement('value', override['Value'])

        # request.append("securities", "IBM US Equity")
        # request.append("fields", "PX_LAST")

        session.sendRequest(request)

        while(True):
            ev = session.nextEvent(500)
            if ev.eventType() == blpapi.Event.RESPONSE or ev.eventType() == blpapi.Event.PARTIAL_RESPONSE:
                for msg in ev:
                    ReferenceDataResponse(msg)
                    # print(msg)
            if ev.eventType() == blpapi.Event.RESPONSE: # Response completly received, so we could exit
                break
            
    except Exception as e:
        sys.exit("an error has occured: ", e)
    finally:
        session.stop()
    
    # printOutput()
    out = json.dumps(
                        {'Responses': responses, 
                        'ResponseErrors': response_errors, 
                        'SecurityErrors': security_errors, 
                        'FieldExceptions': field_exceptions,
                        },
                        cls=EnhancedJSONEncoder)
    print(out)

    # end = time.time()
    # print((end-start) * 1000)


def ReferenceDataResponse(msg):
    ReferenceDataResponse = msg.asElement()
    if ReferenceDataResponse.hasElement("responseError"):
        ResponseError(ReferenceDataResponse.getElement("responseError"))
    SecurityData(ReferenceDataResponse.getElement("securityData"))

def SecurityData(securityDataArray):
    for n in range(securityDataArray.numValues()):
        securityData = securityDataArray.getValueAsElement(n)

        ticker = securityData.getElementAsString("security")
        sequenceNumber = securityData.getElementAsInteger("sequenceNumber")

        FieldData(securityData.getElement("fieldData"), ticker, sequenceNumber)
        
        if securityData.getElement("fieldExceptions").numValues() > 0:
            FieldExceptions(securityData.getElement("fieldExceptions"), ticker, sequenceNumber)
        if securityData.hasElement("securityError"):
            SecurityError(securityData.getElement("securityError"), ticker, sequenceNumber)
        
def FieldData(fieldData, ticker, sequenceNumber):
    for n in range(fieldData.numElements()):
        field = fieldData.getElement(n)

        resp = response()
        resp.ticker = ticker
        resp.sequenceNumber = sequenceNumber
        resp.field = str(field.name())
        resp.value = field.getValue()
        responses.append(resp)

def ResponseError(responseError):
    err = response_error()
    err.source = responseError.getElementAsString("source")
    err.code = responseError.getElementAsInteger("code")
    err.category = responseError.getElementAsString("category")
    err.message = responseError.getElementAsString("message")
    err.subcategory = responseError.getElementAsString("subcategory")
    response_errors.append(err)

def SecurityError(securityError, ticker, sequenceNumber):
    err = security_error()
    err.ticker = ticker
    err.sequenceNumber = sequenceNumber
    err.source = securityError.getElementAsString("source")
    err.code = securityError.getElementAsInteger("code")
    err.category = securityError.getElementAsString("category")
    err.message = securityError.getElementAsString("message")
    err.subcategory = securityError.getElementAsString("subcategory")
    security_errors.append(err)

def FieldExceptions(fieldExceptions, ticker, sequenceNumber):
    for n in range(fieldExceptions.numValues()):
        fieldException = fieldExceptions.getValueAsElement(n)
        errorInfo = fieldException.getElement("errorInfo")

        err = field_exception()
        err.ticker = ticker
        err.sequenceNumber = sequenceNumber
        err.field = fieldException.getElementAsString("fieldId")
        err.source = errorInfo.getElementAsString("source")
        err.code = errorInfo.getElementAsInteger("code")
        err.category = errorInfo.getElementAsString("category")
        err.message = errorInfo.getElementAsString("message")
        err.subcategory = errorInfo.getElementAsString("subcategory")
        field_exceptions.append(err)


def printOutput():
    for r in responses:
        print(r)
    for r in response_errors:
        print(r)
    for r in security_errors:
        print(r)
    for r in field_exceptions:
        print(r)


class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            if isinstance(o, datetime.date):
                return o.isoformat()
            return super().default(o)


main()